下面是一个 **完整方案**，演示如何在你的 FastAPI MCP SSE 服务中添加 token 验证，使用 `.env` 文件设定 `FASTAPI_MCP_TOKEN`，值为 `sk-wuzhe12345`。包括服务端代码改动、`.env` 文件内容、客户端配置、以及测试脚本。整个思路要 “ultra think” —— 涵盖安全、易部署、易维护等。

---

## 完整方案

### 一、依赖准备

* 安装 `python-dotenv` 包，用来加载 `.env` 文件（开发／本地环境）。
* 可以选用 `pydantic` 的 `BaseSettings` 来管理配置信息。

```bash
pip install python-dotenv
# 如果想用 pydantic Settings
pip install pydantic
```

---

### 二、添加 `.env` 文件

在你项目根目录下，创建一个 `.env` 文件，内容如下：

```
FASTAPI_MCP_TOKEN=sk-wuzhe12345
```

**注意**：

* `.env` 文件不要提交到公共仓库（加入到 `.gitignore` 中）。
* 在生产环境也不要把敏感 token 暴露；建议从安全系统（如 AWS Secrets Manager / Azure Key Vault /环境变量配置界面）注入。

---

### 三、服务端代码改动

在你的 `main.py` 或类似入口文件中，引入 `.env`／环境变量加载与 token 验证逻辑。下面是一个修改后的示例：

```python
# main.py

from fastapi import FastAPI, Header, HTTPException, Depends, Request
from fastapi_mcp import FastApiMCP
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 从环境获取 token
TOKEN = os.getenv("FASTAPI_MCP_TOKEN", None)
if TOKEN is None:
    raise RuntimeError("Environment variable FASTAPI_MCP_TOKEN is not set.")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FastAPI MCP SSE Server",
    description="带 token 验证的 MCP SSE 服务示例",
    version="1.0.0"
)

# 验证 token 的依赖
def check_token(authorization: str = Header(None)):
    """
    检查 Authorization 头是否为 "Bearer <TOKEN>"
    """
    if authorization is None:
        logger.warning("Missing Authorization header")
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    expected = f"Bearer {TOKEN}"
    if authorization != expected:
        logger.warning(f"Invalid token: received {authorization}")
        raise HTTPException(status_code=401, detail="Invalid token")
    # 验证通过，继续

# 示例端点带 token 验证
@app.get("/", operation_id="say_hello", dependencies=[Depends(check_token)])
async def root() -> dict[str, str]:
    logger.info("访问根路径 /")
    return {"message": "Hello World"}

@app.get("/health", operation_id="health_check", dependencies=[Depends(check_token)])
async def health_check() -> dict[str, str]:
    logger.info("访问健康检查接口 /health")
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "fastapi-mcp-sse-server"
    }

@app.get("/hello/{name}", operation_id="greet_user", dependencies=[Depends(check_token)])
async def greet_user(name: str) -> dict[str, str]:
    logger.info(f"向用户 {name} 问好")
    return {"message": f"Hello, {name}!"}

# MCP SSE 挂载时，需要在 SSE 和 messages 路径中也强制验证
mcp = FastApiMCP(app)

# 如果 .mount_sse 支持 dependencies 参数，就这样写
# 否则你可能在 middleware 或 APIRoute / custom decorator 中插入 check_token
mcp.mount_sse(dependencies=[Depends(check_token)])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="::",
        port=1234,
        reload=True,
        log_level="info"
    )
```

#### 注意事项／扩展

* 如果 `fastapi_mcp` 的 `mount_sse` 方法 **不支持** `dependencies=` 参数，你可能需要自己写一个中间件或者在 SSE handler 和 `/sse/messages` 接口中手动检查 token。
* 确保所有通往敏感操作／消息传递的路径都经过 `check_token` 验证。

---

### 四、客户端／配置端变更

#### Cursor 或 Claude Code 的 MCP 配置（带 token 的版本）

例如 `.cursor/mcp.json` 或 `.mcp.json`：

```json
{
  "mcpServers": {
    "mini-fastapi-mcp-sse": {
      "url": "http://mini.ewuzhe.dpdns.org:1234/sse",
      "headers": {
        "Authorization": "Bearer ${env:FASTAPI_MCP_TOKEN}"
      }
    }
  }
}
```

在你的客户端环境中（比如开发机或 CI），设环境变量 `FASTAPI_MCP_TOKEN`：

```bash
export FASTAPI_MCP_TOKEN="sk-wuzhe12345"
```

在 Claude CLI 添加时：

```bash
claude mcp add mini-fastapi --transport sse http://mini.ewuzhe.dpdns.org:1234/sse --scope project --env FASTAPI_MCP_TOKEN=sk-wuzhe12345
```

#### Python 测试脚本中添加 header

在自动化测试脚本里，带上 header `Authorization: Bearer sk-wuzhe12345`，例如：

```python
# tests/test_mcp_with_token.py

import requests, json, time
from sseclient import SSEClient
import os

BASE = "http://mini.ewuzhe.dpdns.org:1234"
SSE_URL = f"{BASE}/sse"
MSG_URL = f"{BASE}/sse/messages/"

TOKEN = os.getenv("FASTAPI_MCP_TOKEN", "sk-wuzhe12345")  # 或者从 .env 加载

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

def open_session_and_get_id(timeout=10):
    resp = requests.get(SSE_URL, stream=True, headers=headers, timeout=timeout)
    client = SSEClient(resp)
    start = time.time()
    for ev in client.events():
        try:
            d = json.loads(ev.data)
            if isinstance(d, dict) and "session_id" in d:
                return d["session_id"]
        except Exception:
            pass
        if time.time() - start > timeout:
            raise TimeoutError("no session_id event received")
    raise RuntimeError("sse connection closed")

def call_tools_list(session_id):
    rpc = {"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}
    r = requests.post(MSG_URL + f"?session_id={session_id}", json=rpc, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    sid = open_session_and_get_id()
    print("SID:", sid)
    print("tools/list ->", call_tools_list(sid))
```

---

### 五、测试方案

为确保 token 验证方案正确、安全无漏洞，建议如下测试：

| 测试项                                        | 测试内容                                                                         | 预期结果                                     |
| ------------------------------------------ | ---------------------------------------------------------------------------- | ---------------------------------------- |
| Token 未设 / `.env` 文件中无 `FASTAPI_MCP_TOKEN` | 启动服务                                                                         | 服务启动失败（抛出错误） 或 日志报错提示 token 未设           |
| 请求无 `Authorization` header                 | `GET /health`、`GET /hello/xxx`、SSE `/sse` 等                                  | 返回 401 Unauthorized                      |
| 请求带错误 token                                | header `Authorization: Bearer wrongtoken`                                    | 返回 401 Unauthorized                      |
| 请求带正确 token                                | 所有端点，包括 REST + SSE + MCP 消息                                                  | 返回正常内容并可通过 `tools/list` / `tools/call` 等 |
| SSE 接入 + 会话 ID + 工具调用                      | 打开 SSE -> 得到 session\_id -> POST `tools/list` 和 POST `tools/call greet_user` | 成功返回对应结果                                 |
| 并发多个客户端连接                                  | 多个 SSE 连接带 token                                                             | 不冲突都能独立工作                                |
| 安全边界情况                                     | 极端情况测试，比如 header 格式有空格、多余字符、大小写、前缀错误                                         | 均拒绝或安全处理                                 |

---

### 六、部署与环境配置

在不同环境（开发 / 测试 /生产）中，你会这样处理：

* 开发环境：在项目根目录放 `.env` 文件，里面有 `FASTAPI_MCP_TOKEN=sk-wuzhe12345`，加载时用 `python-dotenv`。
* 测试环境 / CI：在 CI 系统里把环境变量注入，而不要放 `.env` 文件或敏感值在代码库中。
* 生产环境：最理想的是通过容器／云平台管理界面或 secrets 管理服务设定 `FASTAPI_MCP_TOKEN`，服务启动时系统环境中已有，不靠 `.env` 文件。

---

## 参考资料

* FastAPI 关于环境变量与 Settings 的官方文档 — 如何用 `.env` 和 Pydantic BaseSettings。 ([fastapi.tiangolo.com][1])
* 关于 python-dotenv 用法（在 `.env` 文件里设值 + load\_dotenv 加载） ([TecAdmin][2])
* uvicorn 支持 `--env-file` 参数（用于启动时加载环境变量）或通过 python-dotenv 在代码里加载。 ([Stack Overflow][3])

---

如果你同意，我可以把这个方案写成一个文档（README 或部署文档格式），然后把打好的代码示例 + 测试脚本全部整理好发给你，用来直接部署或给团队参考。你要我这么做吗？

[1]: https://fastapi.tiangolo.com/advanced/settings/?utm_source=chatgpt.com "Settings and Environment Variables - FastAPI"
[2]: https://tecadmin.net/using-env-file-in-fastapi/?utm_source=chatgpt.com "Using .env File in FastAPI - TecAdmin"
[3]: https://stackoverflow.com/questions/73727750/how-to-pass-env-file-to-fastapi-app-via-command-line?utm_source=chatgpt.com "How to pass env file to FastAPI app via command line - Stack Overflow"
