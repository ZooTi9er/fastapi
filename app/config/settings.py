"""
配置管理模块

负责环境变量的加载和配置管理。
"""

import os
from dotenv import load_dotenv
from typing import Optional


class Settings:
    """应用配置类"""

    def __init__(self):
        """初始化配置，加载环境变量"""
        # 加载环境变量
        load_dotenv()

        # 应用配置
        self.app_name: str = "FastAPI MCP HTTP Server with Token"
        self.app_version: str = "1.0.0"
        self.app_description: str = "现有 FastAPI + MCP HTTP 服务，带 Token 验证"

        # 认证配置
        self.token: Optional[str] = os.getenv("FASTAPI_MCP_TOKEN")
        if not self.token:
            raise RuntimeError("FASTAPI_MCP_TOKEN 环境变量未设定")

        # 服务器配置
        self.host: str = os.getenv("HOST", "::")
        self.port: int = int(os.getenv("PORT", "1234"))
        self.reload: bool = os.getenv("RELOAD", "True").lower() == "true"
        self.log_level: str = os.getenv("LOG_LEVEL", "info")

        # 日志配置
        self.log_file: str = "logs/app.log"


# 创建全局配置实例
settings = Settings()