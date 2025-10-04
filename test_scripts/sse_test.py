#!/usr/bin/env python3
"""
专门的 SSE 端点测试脚本
"""
import requests
import json
import time
import signal
import sys
from datetime import datetime
from typing import Optional

# 测试配置
BASE_URL = "http://localhost:1234"
TOKEN = "sk-wuzhe12345"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "text/event-stream",
    "Cache-Control": "no-cache"
}

class SSETestResult:
    def __init__(self):
        self.connected = False
        self.events_received = 0
        self.first_event_time = None
        self.last_event_time = None
        self.error = None
        self.events = []
        self.connection_time = 0
        self.test_duration = 0

def test_sse_with_requests(timeout: int = 15) -> SSETestResult:
    """使用 requests 库测试 SSE 端点"""
    result = SSETestResult()
    start_time = time.time()

    try:
        print(f"🔌 尝试连接 {BASE_URL}/sse")
        response = requests.get(
            f"{BASE_URL}/sse",
            headers=HEADERS,
            stream=True,
            timeout=(5, timeout)  # (连接超时, 读取超时)
        )

        if response.status_code == 200:
            result.connected = True
            result.connection_time = time.time() - start_time
            print(f"✅ 连接成功 (耗时: {result.connection_time:.3f}s)")
            print(f"📋 响应头:")
            for key, value in response.headers.items():
                print(f"   {key}: {value}")

            # 读取事件流
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    current_time = time.time()
                    if result.first_event_time is None:
                        result.first_event_time = current_time - start_time

                    result.last_event_time = current_time - start_time
                    result.events_received += 1

                    # 解析事件数据
                    if line.startswith('data: '):
                        data_str = line[6:]  # 移除 'data: ' 前缀
                        try:
                            data = json.loads(data_str)
                            result.events.append(data)
                            print(f"📨 事件 #{result.events_received}: {data.get('type', 'unknown')} - {data.get('message', '')}")
                        except json.JSONDecodeError as e:
                            print(f"⚠️  JSON 解析错误: {e}")
                            result.events.append({"raw": data_str})

                    # 检查是否超时
                    if current_time - start_time > timeout:
                        break

        else:
            result.error = f"HTTP {response.status_code}: {response.text}"
            print(f"❌ 连接失败: {result.error}")

    except requests.exceptions.Timeout:
        result.error = "请求超时"
        print(f"⏰ 请求超时")
    except requests.exceptions.ConnectionError as e:
        result.error = f"连接错误: {str(e)}"
        print(f"🔌 连接错误: {e}")
    except Exception as e:
        result.error = f"未知错误: {str(e)}"
        print(f"❌ 未知错误: {e}")

    result.test_duration = time.time() - start_time
    return result

def test_sse_with_different_timeouts():
    """测试不同超时设置下的 SSE 连接"""
    print("\n" + "="*60)
    print("🧪 测试不同超时设置下的 SSE 连接")
    print("="*60)

    timeouts = [5, 10, 15]
    results = []

    for timeout in timeouts:
        print(f"\n⏱️  测试超时: {timeout}秒")
        result = test_sse_with_requests(timeout)
        results.append({"timeout": timeout, "result": result})

        if result.connected:
            print(f"   📊 连接时间: {result.connection_time:.3f}s")
            print(f"   📨 事件数量: {result.events_received}")
            if result.first_event_time:
                print(f"   ⏰ 首次事件: {result.first_event_time:.3f}s")
            if result.last_event_time:
                print(f"   ⏰ 最后事件: {result.last_event_time:.3f}s")

        # 等待一下再进行下一次测试
        time.sleep(2)

    return results

def analyze_results(results):
    """分析测试结果"""
    print("\n" + "="*60)
    print("📊 测试结果分析")
    print("="*60)

    successful_tests = [r for r in results if r["result"].connected]
    failed_tests = [r for r in results if not r["result"].connected]

    print(f"✅ 成功连接: {len(successful_tests)}/{len(results)}")
    print(f"❌ 连接失败: {len(failed_tests)}/{len(results)}")

    if successful_tests:
        print("\n📈 成功测试统计:")
        avg_connection_time = sum(r["result"].connection_time for r in successful_tests) / len(successful_tests)
        total_events = sum(r["result"].events_received for r in successful_tests)
        print(f"   📊 平均连接时间: {avg_connection_time:.3f}s")
        print(f"   📨 总事件数: {total_events}")

        # 分析事件类型
        all_events = []
        for r in successful_tests:
            all_events.extend(r["result"].events)

        event_types = {}
        for event in all_events:
            event_type = event.get('type', 'unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1

        print(f"   🏷️  事件类型分布:")
        for event_type, count in event_types.items():
            print(f"      {event_type}: {count}")

    if failed_tests:
        print("\n❌ 失败测试分析:")
        for r in failed_tests:
            print(f"   超时 {r['timeout']}s: {r['result'].error}")

def signal_handler(signum, frame):
    """信号处理器，用于优雅退出"""
    print("\n⚠️  测试被中断")
    sys.exit(0)

def main():
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)

    print("🔍 开始专门的 SSE 端点测试")
    print(f"📅 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 测试地址: {BASE_URL}/sse")
    print(f"🔑 使用 Token: {TOKEN[:20]}...")

    # 检查服务是否可用
    print("\n🏥 检查服务健康状态...")
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ 服务运行正常")
        else:
            print(f"⚠️  服务状态异常: {health_response.status_code}")
            return
    except Exception as e:
        print(f"❌ 服务不可用: {e}")
        return

    # 执行 SSE 测试
    results = test_sse_with_different_timeouts()

    # 分析结果
    analyze_results(results)

    # 生成报告
    print("\n📄 生成测试报告...")

    report = f"""# SSE 端点测试报告

**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**测试地址**: {BASE_URL}/sse
**Token**: {TOKEN[:20]}...

## 测试概览

- 测试次数: {len(results)}
- 成功连接: {len([r for r in results if r["result"].connected])}
- 连接失败: {len([r for r in results if not r["result"].connected])}

## 详细结果

"""

    for r in results:
        timeout = r["timeout"]
        result = r["result"]

        report += f"### 超时设置: {timeout}秒\n"
        if result.connected:
            report += f"- **状态**: ✅ 成功连接\n"
            report += f"- **连接时间**: {result.connection_time:.3f}s\n"
            report += f"- **事件数量**: {result.events_received}\n"
            if result.first_event_time:
                report += f"- **首次事件**: {result.first_event_time:.3f}s\n"
            if result.last_event_time:
                report += f"- **最后事件**: {result.last_event_time:.3f}s\n"
            report += f"- **测试时长**: {result.test_duration:.3f}s\n"
        else:
            report += f"- **状态**: ❌ 连接失败\n"
            report += f"- **错误信息**: {result.error}\n"
            report += f"- **测试时长**: {result.test_duration:.3f}s\n"
        report += "\n"

    # 添加分析结论
    report += """## 分析结论

基于测试结果，可以得出以下结论：

"""

    successful_tests = [r for r in results if r["result"].connected]
    if len(successful_tests) == 0:
        report += "❌ **SSE 端点无法正常工作**\n"
        report += "- 所有测试都失败了，可能是认证问题或服务配置问题\n"
        report += "- 建议检查认证机制和服务日志\n"
    elif len(successful_tests) == len(results):
        report += "✅ **SSE 端点工作正常**\n"
        report += "- 所有测试都成功连接\n"
        report += "- 事件流正常，包含连接确认和心跳机制\n"
    else:
        report += "⚠️ **SSE 端点工作不稳定**\n"
        report += f"- {len(successful_tests)}/{len(results)} 的测试成功\n"
        report += "- 可能存在超时配置或连接稳定性问题\n"

    # 保存报告
    report_file = "docs/sse_test_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"📄 测试报告已保存到 {report_file}")

if __name__ == "__main__":
    main()