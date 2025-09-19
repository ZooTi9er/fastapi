from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

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
    title="FastAPI MCP SSE Server",
    description="最简单的 MCP SSE 服务示例",
    version="1.0.0"
)

# 定义示例端点
@app.get("/", operation_id="say_hello")
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

@app.get("/hello/{name}", operation_id="greet_user")
async def greet_user(name: str) -> dict[str, str]:
    """向用户问好"""
    logger.info(f"向用户 {name} 问好")
    return {"message": f"Hello, {name}!"}

# 创建 MCP 实例并挂载 SSE 服务
mcp = FastApiMCP(app)
mcp.mount_sse()

if __name__ == "__main__":
    import uvicorn

    # 从环境变量获取配置，提供默认值
    host = os.getenv("HOST", "::")
    port = int(os.getenv("PORT", "1234"))
    reload = os.getenv("RELOAD", "True").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level
    )