import os
from fastapi import FastAPI, Header, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi_mcp import FastApiMCP
from dotenv import load_dotenv
import logging
from datetime import datetime

# 加载 .env 文件
load_dotenv()

# 获取 token
TOKEN = os.getenv("FASTAPI_MCP_TOKEN")
if not TOKEN:
    raise RuntimeError("FASTAPI_MCP_TOKEN 环境变量未设定")

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

# 创建 FastAPI 应用
app = FastAPI(
    title="FastAPI MCP SSE Server with Token",
    version="1.0.0",
    description="现有 FastAPI + MCP SSE 服务，带 Token 验证"
)

# 认证依赖
def check_token(authorization: str = Header(None)):
    """
    验证 Authorization 头是否像 "Bearer <token>" 并与 FASTAPI_MCP_TOKEN 匹配
    """
    if authorization is None:
        logger.warning("Missing Authorization header")
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    expected = f"Bearer {TOKEN}"
    if authorization != expected:
        logger.warning(f"Invalid token received: {authorization[:20]}...")
        raise HTTPException(status_code=401, detail="Invalid token")

    logger.info("Token authentication successful")
    return True

# 定义示例端点
@app.get("/", operation_id="say_hello", dependencies=[Depends(check_token)])
async def root() -> dict[str, str]:
    """根路径，返回 Hello World"""
    logger.info("访问根路径 /")
    return {"message": "Hello World"}

@app.get("/health", operation_id="health_check")
async def health_check() -> dict[str, str]:
    """健康检查接口"""
    logger.info("访问健康检查接口 /health")
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "fastapi-mcp-sse-server"
    }

@app.get("/hello/{name}", operation_id="greet_user", dependencies=[Depends(check_token)])
async def greet_user(name: str) -> dict[str, str]:
    """向用户问好"""
    logger.info(f"向用户 {name} 问好")
    return {"message": f"Hello, {name}!"}

# 创建 MCP 实例并挂载 SSE 服务
mcp = FastApiMCP(app)

# mount_sse 方法是否支持 dependencies 参数取决于 fastapi_mcp 库版本。
# 如果支持，可以这样做：
# 添加全局认证中间件保护SSE端点
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # 对SSE相关路径进行认证检查
    if request.url.path.startswith("/sse"):
        authorization = request.headers.get("Authorization")
        if not authorization:
            logger.warning("SSE请求缺少Authorization头")
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing Authorization header"}
            )

        expected = f"Bearer {TOKEN}"
        if authorization != expected:
            logger.warning(f"SSE请求无效token: {authorization[:20]}...")
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"}
            )

        logger.info("SSE请求认证成功")

    response = await call_next(request)
    return response

# 挂载MCP SSE服务器（不带dependencies参数）
try:
    mcp.mount_sse()
    logger.info("MCP SSE 挂载成功，通过中间件进行 token 验证")
except Exception as e:
    logger.error(f"MCP SSE 挂载失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="::",
        port=1234,
        reload=True,
        log_level="info"
    )