# FastAPI 集成 Model Context Protocol (MCP) 服务说明文档

## 引言

本说明文档旨在指导您如何在现有的 FastAPI 应用程序中集成 `fastapi_mcp` 库，从而将您的 FastAPI 端点暴露为 Model Context Protocol (MCP) 工具。通过集成 `fastapi_mcp`，您可以让 AI 代理（如大型语言模型 LLMs）更方便、安全地调用您的 API 服务。

`fastapi_mcp` 是一个 FastAPI 原生库，它能自动保留您端点的 OpenAPI 规范和文档，并提供灵活的部署选项和内置的认证支持。

## 安装

要安装 `fastapi_mcp`，推荐使用 `pip` 或 `uv` 包管理器。

**使用 pip:**

```bash
pip install fastapi-mcp
```

**使用 uv (推荐):**

```bash
uv add fastapi-mcp
```

## 基本用法

将 `fastapi_mcp` 集成到您的 FastAPI 应用程序非常简单，只需几行代码即可完成。以下是一个基本示例：

```python
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

# 您的 FastAPI 应用程序实例
app = FastAPI(
    title="My Awesome API",
    description="This is a simple FastAPI application."
)

# 定义一些示例 FastAPI 端点
@app.get("/hello", operation_id="say_hello")
async def say_hello():
    return {"message": "Hello from FastAPI!"}

@app.get("/items/{item_id}", operation_id="get_item_by_id")
async def get_item(item_id: int):
    return {"item_id": item_id, "name": f"Item {item_id}"}

# 实例化 FastApiMCP
# 将您的 FastAPI 应用程序实例传递给 FastApiMCP
mcp = FastApiMCP(app)

# 挂载 MCP 服务
# 这将自动在 `/mcp` 路径下暴露您的 FastAPI 端点作为 MCP 工具
mcp.mount_http()

# 您可以通过 uvicorn 运行您的应用程序：
# uvicorn main:app --reload
```

在上述代码中：

1.  我们导入了 `FastAPI` 和 `FastApiMCP`。
2.  创建了一个 `FastAPI` 应用程序实例 `app`。
3.  定义了一些带有 `operation_id` 的 FastAPI 端点。`operation_id` 将作为 MCP 工具的名称。
4.  实例化 `FastApiMCP`，并将 `app` 传递给它。
5.  调用 `mcp.mount_http()` 来挂载 MCP 服务。默认情况下，MCP 服务将通过 HTTP 传输方式在 `/mcp` 路径下可用。

## 高级配置

`fastapi_mcp` 提供了多种高级配置选项，以满足不同的需求：

### 认证和授权

`fastapi_mcp` 支持 OAuth 2 流程和基本的令牌传递。您可以配置 `AuthConfig` 来集成现有的 FastAPI 依赖项和 OAuth 提供者。

示例 (OAuth 配置):

```python
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def verify_auth(token: str = Depends(oauth2_scheme)):
    # 在这里实现您的令牌验证逻辑
    if token != "my-secret-token":
        raise HTTPException(status_code=400, detail="Invalid token")
    return token

# ... (FastAPI app and endpoints definition) ...

mcp = FastApiMCP(
    app,
    name="MCP With OAuth",
    auth_config=AuthConfig(
        issuer=f"https://auth.example.com/",
        authorize_url=f"https://auth.example.com/authorize",
        oauth_metadata_url=f"https://auth.example.com/.well-known/oauth-authorization-server",
        audience="my-audience",
        client_id="my-client-id",
        client_secret="my-client-secret",
        dependencies=[Depends(verify_auth)], # 使用 FastAPI 依赖进行认证
        setup_proxies=True,
    ),
)
mcp.mount_http()
```

### 传输方式

`fastapi_mcp` 支持 HTTP 传输（推荐）和 SSE 传输（用于向后兼容）。HTTP 传输实现了最新的 MCP Streamable HTTP 规范，提供更好的会话管理。

*   **HTTP 传输 (推荐)**:
    ```python
    mcp.mount_http()
    ```
*   **SSE 传输 (向后兼容)**:
    ```python
    mcp.mount_sse()
    ```

### 自定义工具命名和暴露

`fastapi_mcp` 使用 FastAPI 路由的 `operation_id` 作为 MCP 工具的名称。为了清晰起见，强烈建议为您的 FastAPI 路由显式指定 `operation_id`。

您还可以通过 `include_operations`、`exclude_operations` 或标签来控制哪些 FastAPI 端点作为 MCP 工具暴露。

示例 (自定义工具命名):

```python
@app.get("/users/{user_id}", operation_id="get_user_information")
async def read_user(user_id: int):
    return {"user_id": user_id}
```

示例 (包含特定操作):

```python
mcp = FastApiMCP(
    app,
    include_operations=["get_user_information", "create_new_user"]
)
mcp.mount_http()
```

## 部署

您可以选择将 MCP 服务器与您的 FastAPI 应用程序一起部署，也可以将其分离部署。分离部署允许您从一个 API 应用程序创建 MCP 服务器，然后将其挂载到另一个独立的 FastAPI 应用程序上。

示例 (分离部署):

```python
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

api_app = FastAPI() # 您的 API 应用程序
mcp_app = FastAPI() # 专门用于托管 MCP 服务的应用程序

mcp = FastApiMCP(api_app)
mcp.mount_http(mcp_app) # 将 MCP 服务挂载到 mcp_app

# 然后分别运行 api_app 和 mcp_app
# uvicorn api_main:api_app --port 8000
# uvicorn mcp_main:mcp_app --port 8001
```

## 结论

通过 `fastapi_mcp`，您可以轻松地将您的 FastAPI 应用程序转换为强大的 MCP 服务，使其能够与各种 AI 代理进行交互。遵循本指南中的步骤和最佳实践，您将能够高效地构建和部署您的 MCP 服务。