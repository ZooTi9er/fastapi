from fastapi import FastAPI
import logging
import os
from datetime import datetime

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
    title="FastAPI Hello World",
    description="最简单的 FastAPI 测试程序",
    version="1.0.0"
)

@app.get("/")
async def root() -> dict[str, str]:
    """根路径，返回 Hello World"""
    logger.info("访问根路径 /")
    return {"message": "Hello World"}

@app.get("/health")
async def health_check() -> dict[str, str]:
    """健康检查接口"""
    logger.info("访问健康检查接口 /health")
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "fastapi-hello-world"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="::",
        port=1234,
        reload=True,
        log_level="info"
    )