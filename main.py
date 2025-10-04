import os
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi_mcp import FastApiMCP
from datetime import datetime
import asyncio
import json

# 导入自定义模块
from app.auth.dependencies import get_current_user
from app.config.settings import settings
from app.utils.logging import setup_logging, get_logger

# 设置日志
setup_logging(settings.log_file, settings.log_level)
logger = get_logger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description
)

# 定义示例端点
@app.get("/", operation_id="say_hello", dependencies=[Depends(get_current_user)])
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
        "service": "fastapi-mcp-http-server"
    }

@app.get("/hello/{name}", operation_id="greet_user", dependencies=[Depends(get_current_user)])
async def greet_user(name: str) -> dict[str, str]:
    """向用户问好"""
    logger.info(f"向用户 {name} 问好")
    return {"message": f"Hello, {name}!"}

@app.get("/sse", operation_id="sse_endpoint", dependencies=[Depends(get_current_user)])
async def sse_endpoint():
    """SSE (Server-Sent Events) 端点，提供实时事件流"""
    logger.info("访问SSE端点 /sse")

    async def event_stream():
        """生成事件流"""
        client_connected = False
        try:
            # 发送初始连接消息
            yield f"data: {json.dumps({'type': 'connected', 'message': 'SSE连接已建立', 'timestamp': datetime.now().isoformat()})}\n\n"
            client_connected = True
            logger.info("SSE客户端连接成功")

            # 定期发送心跳消息
            counter = 0
            while True:
                await asyncio.sleep(10)  # 每10秒发送一次心跳
                counter += 1
                heartbeat = {
                    'type': 'heartbeat',
                    'message': f'心跳 #{counter}',
                    'timestamp': datetime.now().isoformat(),
                    'counter': counter
                }
                yield f"data: {json.dumps(heartbeat)}\n\n"
                logger.debug(f"发送心跳 #{counter}")

        except asyncio.CancelledError:
            logger.info("SSE连接被客户端取消")
            if client_connected:
                yield f"data: {json.dumps({'type': 'disconnected', 'message': '连接已断开', 'timestamp': datetime.now().isoformat()})}\n\n"
        except Exception as e:
            logger.error(f"SSE流异常: {str(e)}")
            error_msg = {
                'type': 'error',
                'message': f'SSE流异常: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
            try:
                yield f"data: {json.dumps(error_msg)}\n\n"
            except Exception:
                logger.error("无法发送错误消息到客户端")

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream; charset=utf-8",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Authorization, Cache-Control",
            "Access-Control-Allow-Methods": "GET",
            "X-Accel-Buffering": "no"  # 禁用 nginx 缓冲
        }
    )

# 创建 MCP 实例并挂载 HTTP 服务
mcp = FastApiMCP(app)

# 挂载MCP HTTP服务器（推荐方式）
try:
    mcp.mount_http()
    logger.info("MCP HTTP 挂载成功")
except Exception as e:
    logger.error(f"MCP HTTP 挂载失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn

    # 使用配置类中的设置
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level
    )