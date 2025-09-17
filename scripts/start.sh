#!/bin/bash

# FastAPI 启动脚本
# 确保在正确的目录中运行
cd "$(dirname "$0")/.."

# 检查虚拟环境是否存在
if [ ! -d ".venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv .venv
fi

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 创建日志目录
mkdir -p logs

# 启动 FastAPI 应用
echo "启动 FastAPI 应用..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload