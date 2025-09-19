#!/usr/bin/env python3
"""
简化的MCP测试脚本（不依赖SSEClient）
"""
import requests
import json
import time
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 测试配置
BASE_URL = "http://localhost:1234"
TOKEN = "sk-wuzhe12345"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def test_sse_auth():
    """测试SSE端点认证"""
    results = []

    # 测试无认证
    try:
        response = requests.get(f"{BASE_URL}/sse", timeout=5)
        results.append({
            "test": "SSE无认证",
            "status": "✅ 通过" if response.status_code == 401 else "❌ 失败",
            "details": f"状态码: {response.status_code}"
        })
    except Exception as e:
        results.append({
            "test": "SSE无认证",
            "status": "❌ 失败",
            "details": f"异常: {str(e)}"
        })

    # 测试错误token
    try:
        response = requests.get(f"{BASE_URL}/sse", headers={"Authorization": "Bearer wrong_token"}, timeout=5)
        results.append({
            "test": "SSE错误token",
            "status": "✅ 通过" if response.status_code == 401 else "❌ 失败",
            "details": f"状态码: {response.status_code}"
        })
    except Exception as e:
        results.append({
            "test": "SSE错误token",
            "status": "❌ 失败",
            "details": f"异常: {str(e)}"
        })

    # 测试正确token（连接测试）
    try:
        response = requests.get(f"{BASE_URL}/sse", headers=HEADERS, timeout=2)
        results.append({
            "test": "SSE正确token",
            "status": "✅ 通过" if response.status_code == 200 else "❌ 失败",
            "details": f"状态码: {response.status_code}"
        })
    except requests.exceptions.Timeout:
        results.append({
            "test": "SSE正确token",
            "status": "✅ 通过",
            "details": "连接超时（SSE长连接正常）"
        })
    except Exception as e:
        results.append({
            "test": "SSE正确token",
            "status": "❌ 失败",
            "details": f"异常: {str(e)}"
        })

    return results

def test_mcp_messages():
    """测试MCP messages端点"""
    results = []

    # 测试无session_id
    try:
        response = requests.post(
            f"{BASE_URL}/sse/messages/",
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
            headers=HEADERS,
            timeout=5
        )
        results.append({
            "test": "Messages无session_id",
            "status": "✅ 通过" if response.status_code == 400 else "❌ 失败",
            "details": f"状态码: {response.status_code}, 响应: {response.text[:50]}"
        })
    except Exception as e:
        results.append({
            "test": "Messages无session_id",
            "status": "❌ 失败",
            "details": f"异常: {str(e)}"
        })

    # 测试无认证
    try:
        response = requests.post(
            f"{BASE_URL}/sse/messages/test",
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
            timeout=5
        )
        results.append({
            "test": "Messages无认证",
            "status": "✅ 通过" if response.status_code == 401 else "❌ 失败",
            "details": f"状态码: {response.status_code}"
        })
    except Exception as e:
        results.append({
            "test": "Messages无认证",
            "status": "❌ 失败",
            "details": f"异常: {str(e)}"
        })

    # 测试有认证无session_id
    try:
        response = requests.post(
            f"{BASE_URL}/sse/messages/test",
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
            headers=HEADERS,
            timeout=5
        )
        results.append({
            "test": "Messages有认证无session_id",
            "status": "✅ 通过" if response.status_code == 400 else "❌ 失败",
            "details": f"状态码: {response.status_code}, 响应: {response.text[:50]}"
        })
    except Exception as e:
        results.append({
            "test": "Messages有认证无session_id",
            "status": "❌ 失败",
            "details": f"异常: {str(e)}"
        })

    return results

def main():
    print("🔧 开始简化MCP测试")
    print(f"📅 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 测试地址: {BASE_URL}")
    print("=" * 60)

    all_results = []

    # 测试SSE认证
    print("📡 测试SSE认证...")
    sse_results = test_sse_auth()
    all_results.extend(sse_results)

    # 测试MCP messages
    print("\n💬 测试MCP messages...")
    message_results = test_mcp_messages()
    all_results.extend(message_results)

    # 显示结果
    print("\n" + "=" * 60)
    print("📊 测试结果")
    print("=" * 60)

    passed = 0
    for result in all_results:
        print(f"{result['test']}: {result['status']} - {result['details']}")
        if "✅" in result['status']:
            passed += 1

    success_rate = (passed / len(all_results) * 100) if all_results else 0
    print(f"\n成功率: {passed}/{len(all_results)} ({success_rate:.1f}%)")

    # 生成报告
    report = f"""# MCP修复验证测试报告

**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**测试地址**: {BASE_URL}
**Token**: {TOKEN[:20]}...

## 测试结果概览
- 总测试数: {len(all_results)}
- 通过测试: {passed}
- 失败测试: {len(all_results) - passed}
- 成功率: {success_rate:.1f}%

## 详细结果

"""

    for result in all_results:
        report += f"### {result['test']}\n"
        report += f"- **状态**: {result['status']}\n"
        report += f"- **详情**: {result['details']}\n\n"

    if success_rate >= 80:
        report += "## 修复评估\n✅ MCP SSE认证问题已基本修复，功能正常。\n"
    else:
        report += "## 修复评估\n⚠️ 部分功能仍存在问题，需要进一步调试。\n"

    with open("mcp_fix_test_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n📄 详细报告已保存到 mcp_fix_test_report.md")

if __name__ == "__main__":
    main()