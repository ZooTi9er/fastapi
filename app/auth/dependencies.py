"""
认证依赖模块

提供统一的认证机制，避免重复实现。
"""

from fastapi import Header, HTTPException, Depends
import logging

logger = logging.getLogger(__name__)


def get_current_user(authorization: str = Header(None)) -> bool:
    """
    验证 Authorization 头是否像 "Bearer <token>" 并与 FASTAPI_MCP_TOKEN 匹配

    Args:
        authorization: Authorization header value

    Returns:
        bool: 认证成功返回 True

    Raises:
        HTTPException: 认证失败时抛出 401 错误
    """
    if authorization is None:
        logger.warning("Missing Authorization header")
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    # 从环境变量获取 token
    import os
    token = os.getenv("FASTAPI_MCP_TOKEN")
    if not token:
        logger.error("FASTAPI_MCP_TOKEN 环境变量未设定")
        raise HTTPException(status_code=500, detail="Server configuration error")

    expected = f"Bearer {token}"
    if authorization != expected:
        logger.warning(f"Invalid token received: {authorization[:20]}...")
        raise HTTPException(status_code=401, detail="Invalid token")

    logger.info("Token authentication successful")
    return True