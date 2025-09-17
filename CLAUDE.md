# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个简单的 FastAPI 测试项目，用于演示 FastAPI 的基本功能和 MCP (Model Context Protocol) 集成。

## 常用命令

### 启动应用
```bash
# 使用脚本启动（推荐）
./scripts/start.sh

# 或者直接使用 uvicorn 启动
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 或者运行 main.py
python main.py
```

### 依赖管理
```bash
# 使用 uv 安装依赖（推荐）
uv add fastapi uvicorn[standard]

# 或者使用 pip
pip install -r requirements.txt
```

## 项目架构

### 核心文件
- `main.py` - 主应用程序文件，包含 FastAPI 应用定义和基础路由
- `requirements.txt` - 项目依赖文件
- `scripts/start.sh` - 应用启动脚本

### 应用结构
- **FastAPI App**: 主应用实例，配置了基本的元数据
- **日志系统**: 同时输出到文件 (`logs/app.log`) 和控制台
- **路由**: 包含根路径 `/` 和健康检查 `/health` 端点
- **开发服务器**: 使用 uvicorn，支持热重载

### 端点说明
- `GET /` - 返回简单的 Hello World 消息
- `GET /health` - 健康检查端点，返回服务状态和时间戳

## 开发规范

### Python 开发
- 使用 `.venv` 作为虚拟环境目录名
- 优先使用 `uv` 进行依赖管理
- 保持强类型标注
- 使用中文注释和文档字符串

### 日志配置
- 日志级别设置为 INFO
- 日志同时输出到文件和控制台
- 日志文件存储在 `logs/` 目录下

### 启动脚本
- 自动创建和激活虚拟环境
- 自动安装依赖
- 自动创建日志目录
- 使用 uvicorn 启动开发服务器

## MCP 集成

项目包含 `fastapi_mcp_integration_guide.md` 文档，详细说明了如何将 FastAPI 应用与 Model Context Protocol (MCP) 集成，使 AI 代理能够调用您的 API 端点。

### 集成要点
- 使用 `fastapi-mcp` 库
- 通过 `operation_id` 定义 MCP 工具名称
- 支持 HTTP 和 SSE 传输方式
- 内置 OAuth 认证支持
- 支持分离部署模式

## 环境配置

### 开发环境
- Python 3.8+
- FastAPI 0.115.6
- Uvicorn 0.32.1

### 端口配置
- 默认端口：8000（脚本启动）
- main.py 中配置为 1234

## 部署注意事项

- 生产环境建议使用生产级 WSGI 服务器（如 Gunicorn）
- 配置适当的环境变量
- 使用适当的日志级别
- 考虑添加 API 认证和限流机制