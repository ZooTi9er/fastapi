# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个 FastAPI MCP SSE 服务项目，演示了如何将 FastAPI 应用与 Model Context Protocol (MCP) 集成，包含 Token 认证和实时事件流功能。

## 常用命令

### 启动应用
```bash
# 使用脚本启动（推荐）
./scripts/start.sh

# 或者直接运行 main.py（使用 .env 配置）
python main.py
```

### 依赖管理
```bash
# 使用 uv 安装依赖（推荐）
uv add fastapi uvicorn[standard] fastapi-mcp python-dotenv

# 或者使用 pip
pip install -r requirements.txt
```

### 测试命令
```bash
# 运行所有测试脚本
python -m pytest test_scripts/ -v

# 运行特定测试
python test_scripts/auth_test.py      # 认证测试
python test_scripts/mcp_test.py       # MCP功能测试
python test_scripts/mcp_fix_test.py   # MCP修复测试
python test_scripts/sse_test.py       # SSE事件流测试
python test_scripts/simple_test.py    # 基础功能测试
```

### 端点测试
```bash
# 健康检查（公开访问）
curl http://localhost:1234/health

# 根路径（需要认证）
curl -H "Authorization: Bearer sk-wuzhe12345" http://localhost:1234/

# 个性化问候（需要认证）
curl -H "Authorization: Bearer sk-wuzhe12345" http://localhost:1234/hello/yourname

# SSE 端点（需要认证，会持续发送事件）
curl -H "Authorization: Bearer sk-wuzhe12345" http://localhost:1234/sse

# MCP 端点（需要特定的 Accept 头和会话ID）
curl -H "Accept: text/event-stream" -H "Authorization: Bearer sk-wuzhe12345" http://localhost:1234/mcp
```

## 项目架构

### 核心模块结构
```
app/
├── auth/
│   ├── __init__.py
│   └── dependencies.py      # Token 认证依赖 (get_current_user)
├── config/
│   ├── __init__.py
│   └── settings.py          # 环境配置管理 (Settings 类)
├── utils/
│   ├── __init__.py
│   └── logging.py           # 日志配置 (setup_logging, get_logger)
└── __init__.py
```

### 主要文件
- `main.py` - 主应用，包含 FastAPI 应用、路由定义、SSE端点和 MCP 集成
- `requirements.txt` - 项目依赖（FastAPI 0.115.6, Uvicorn 0.32.1, fastapi-mcp, python-dotenv）
- `scripts/start.sh` - 启动脚本，自动处理虚拟环境和依赖安装
- `.env` - 环境配置文件
- `app/` - 应用模块，采用分层架构
- `test_scripts/` - 测试脚本集合，包含认证、MCP、SSE等功能测试

### 架构特点
- **模块化设计**: 认证、配置、日志功能分离到不同模块，每个模块职责单一
- **统一认证**: 通过 `app.auth.dependencies.get_current_user` 实现 Bearer Token 认证，所有受保护端点统一使用
- **配置管理**: 使用 `app.config.settings.Settings` 类集中管理环境变量，启动时自动验证必需配置
- **日志系统**: 通过 `app.utils.logging` 统一日志配置，同时输出到文件(`logs/app.log`)和控制台
- **MCP 集成**: 使用 `fastapi-mcp` 库，通过 `FastApiMCP(app)` 和 `mcp.mount_http()` 在 `/mcp` 端点提供 MCP 服务
- **SSE 支持**: `/sse` 端点提供实时事件流，包含连接确认、10秒心跳间隔、断开连接处理和异常处理
- **优雅的错误处理**: 统一的异常处理机制，包含详细的日志记录

### 端点说明
- `GET /` - 根路径，返回 Hello World（需要认证）
- `GET /health` - 健康检查，公开访问
- `GET /hello/{name}` - 个性化问候（需要认证）
- `GET /sse` - SSE 实时事件流，10秒心跳间隔（需要认证）
- `/mcp` - MCP HTTP 服务器端点（需要 Accept: text/event-stream 头和认证）

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

### 启动脚本 (scripts/start.sh)
- 自动检测并创建 `.venv` 虚拟环境（如果不存在）
- 自动安装 `uv` 包管理器（如果未安装）
- 根据 `pyproject.toml` 或 `requirements.txt` 自动安装依赖
- 自动创建 `logs/` 目录
- 使用 `python main.py` 启动应用（从 `.env` 读取配置）

## MCP 集成

项目包含 `fastapi_mcp_integration_guide.md` 文档，详细说明了如何将 FastAPI 应用与 Model Context Protocol (MCP) 集成，使 AI 代理能够调用您的 API 端点。

### 集成要点
- 使用 `fastapi-mcp` 库
- 通过 `operation_id` 定义 MCP 工具名称
- 支持 HTTP 和 SSE 传输方式
- 内置 OAuth 认证支持
- 支持分离部署模式

## 环境配置

### 开发环境要求
- Python 3.8+
- uv（推荐）或 pip 包管理器

### 核心依赖版本
- **FastAPI** 0.115.6 - Web 框架
- **Uvicorn[standard]** 0.32.1 - ASGI 服务器
- **fastapi-mcp** - MCP 集成库（最新版本）
- **python-dotenv** - 环境变量管理

### 必需环境变量
通过 `.env` 文件配置以下参数：
- `FASTAPI_MCP_TOKEN` - API 认证令牌（必需，应用启动时验证）
- `HOST` - 监听地址（默认：::）
- `PORT` - 监听端口（默认：1234）
- `RELOAD` - 开发模式热重载（默认：True）
- `LOG_LEVEL` - 日志级别（默认：info）

### 端口和网络
- 默认端口：1234（可通过 .env 文件配置）
- 默认监听地址：::（同时支持 IPv4 和 IPv6）

## 部署注意事项

- 生产环境建议使用生产级 WSGI 服务器（如 Gunicorn）
- 配置适当的环境变量
- 使用适当的日志级别
- 考虑添加 API 认证和限流机制