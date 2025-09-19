#!/usr/bin/env python3
"""
简化的FastAPI测试脚本
"""
import requests
import json
import time
from datetime import datetime

# 测试配置
BASE_URL = "http://localhost:1234"
TOKEN = "sk-wuzhe12345"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def test_endpoint(url, method="GET", headers=None, data=None, timeout=5):
    """测试单个端点"""
    try:
        start_time = time.time()
        response = requests.request(method, url, headers=headers, json=data, timeout=timeout)
        response_time = time.time() - start_time

        return {
            "status_code": response.status_code,
            "response_time": response_time,
            "content": response.text[:200] if response.text else "",
            "headers": dict(response.headers),
            "success": True
        }
    except requests.exceptions.Timeout:
        return {"success": False, "error": "请求超时", "response_time": timeout}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "连接错误"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    print("🔍 开始简化测试 FastAPI 服务")
    print(f"📅 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 测试地址: {BASE_URL}")
    print("=" * 60)

    results = []

    # 测试1: 健康检查（应该不需要token）
    print("1️⃣ 测试 /health 端点（无认证）...")
    result = test_endpoint(f"{BASE_URL}/health")
    results.append({"endpoint": "/health", "auth": False, "result": result})
    print(f"   结果: {result}")

    # 测试2: 根路径（有认证）
    print("\n2️⃣ 测试 / 端点（有认证）...")
    result = test_endpoint(f"{BASE_URL}/", headers=HEADERS)
    results.append({"endpoint": "/", "auth": True, "result": result})
    print(f"   结果: {result}")

    # 测试3: 根路径（无认证）
    print("\n3️⃣ 测试 / 端点（无认证）...")
    result = test_endpoint(f"{BASE_URL}/")
    results.append({"endpoint": "/", "auth": False, "result": result})
    print(f"   结果: {result}")

    # 测试4: SSE端点（有认证）
    print("\n4️⃣ 测试 /sse 端点（有认证）...")
    result = test_endpoint(f"{BASE_URL}/sse", headers=HEADERS)
    results.append({"endpoint": "/sse", "auth": True, "result": result})
    print(f"   结果: {result}")

    # 测试5: hello端点（有认证）
    print("\n5️⃣ 测试 /hello/test 端点（有认证）...")
    result = test_endpoint(f"{BASE_URL}/hello/test", headers=HEADERS)
    results.append({"endpoint": "/hello/test", "auth": True, "result": result})
    print(f"   结果: {result}")

    # 生成报告
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)

    success_count = 0
    for test in results:
        endpoint = test["endpoint"]
        auth = "有认证" if test["auth"] else "无认证"
        result = test["result"]

        if result["success"]:
            status = f"✅ {result['status_code']}"
            if result["status_code"] == 200:
                success_count += 1
        else:
            status = f"❌ {result['error']}"

        print(f"{endpoint} ({auth}): {status}")

    print(f"\n成功率: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")

    # 保存详细结果
    report = f"""# FastAPI 服务测试报告

**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**测试地址**: {BASE_URL}
**Token**: {TOKEN[:20]}...

## 测试结果概览
- 总测试数: {len(results)}
- 成功测试: {success_count}
- 失败测试: {len(results) - success_count}
- 成功率: {success_count/len(results)*100:.1f}%

## 详细结果

"""
    for test in results:
        endpoint = test["endpoint"]
        auth = "有认证" if test["auth"] else "无认证"
        result = test["result"]

        report += f"### {endpoint} ({auth})\n"
        if result["success"]:
            report += f"- **状态**: ✅ 成功\n"
            report += f"- **状态码**: {result['status_code']}\n"
            report += f"- **响应时间**: {result['response_time']:.3f}s\n"
            if result["content"]:
                report += f"- **响应内容**: {result['content']}\n"
        else:
            report += f"- **状态**: ❌ 失败\n"
            report += f"- **错误**: {result['error']}\n"
        report += "\n"

    with open("simple_test_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n📄 详细报告已保存到 simple_test_report.md")

    # 分析和建议
    print("\n💡 分析和建议")
    print("-" * 30)
    if success_count == len(results):
        print("🎉 所有测试通过！服务运行正常。")
    elif success_count == 0:
        print("🚨 所有测试失败！服务可能未启动或配置错误。")
    else:
        print("⚠️ 部分测试失败，请检查服务配置。")

        # 检查认证问题
        auth_success = sum(1 for test in results if test["auth"] and test["result"]["success"])
        noauth_success = sum(1 for test in results if not test["auth"] and test["result"]["success"])

        if auth_success == 0 and noauth_success > 0:
            print("🔐 认证可能有问题：无认证的端点正常，有认证的端点失败。")
        elif auth_success > 0 and noauth_success == 0:
            print("🔓 认证配置正常，但公开端点可能有问题。")

if __name__ == "__main__":
    main()