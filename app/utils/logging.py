"""
日志配置模块

提供统一的日志配置功能。
"""

import logging
import os
from datetime import datetime


def setup_logging(log_file: str = "logs/app.log", log_level: str = "INFO") -> None:
    """
    设置日志配置

    Args:
        log_file: 日志文件路径
        log_level: 日志级别
    """
    # 创建日志目录
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # 配置日志
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    # 记录启动信息
    logger = logging.getLogger(__name__)
    logger.info(f"日志系统初始化完成 - {datetime.now().isoformat()}")


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志器

    Args:
        name: 日志器名称

    Returns:
        logging.Logger: 日志器实例
    """
    return logging.getLogger(name)