#!/usr/bin/env python3
"""
MCP SSE 协议测试脚本
"""
import requests
import json
import time
import logging
from typing import Dict, Any, Optional
try:
    from sseclient import SSEClient
    SSE_AVAILABLE = True
except ImportError:
    SSE_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPTestSuite:
    def __init__(self, base_url: str = "http://localhost:1234", token: str = "sk-wuzhe12345"):
        self.base_url = base_url
        self.token = token
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.results = []

    def add_result(self, test_name: str, passed: bool, details: str = "", session_id: str = None):
        """添加测试结果"""
        self.results.append({
            "test_name": test_name,
            "passed": passed,
            "details": details,
            "session_id": session_id,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        })

    def test_sse_connection(self) -> Optional[str]:
        """测试SSE连接并获取session_id"""
        if not SSE_AVAILABLE:
            logger.warning("SSEClient不可用，跳过SSE测试")
            self.add_result("sse_connection", False, "SSEClient库未安装")
            return None

        sse_url = f"{self.base_url}/sse"
        try:
            logger.info("正在建立SSE连接...")
            response = requests.get(sse_url, headers=self.headers, stream=True, timeout=10)

            if response.status_code != 200:
                self.add_result("sse_connection", False, f"连接失败，状态码: {response.status_code}")
                return None

            client = SSEClient(response)
            session_id = None
            start_time = time.time()
            timeout = 15  # 15秒超时

            for event in client.events():
                try:
                    data = json.loads(event.data)
                    logger.info(f"收到SSE事件: {event.event} - {data}")

                    if isinstance(data, dict) and "session_id" in data:
                        session_id = data["session_id"]
                        self.add_result("sse_connection", True, f"成功获取session_id: {session_id}", session_id)
                        break

                    if time.time() - start_time > timeout:
                        self.add_result("sse_connection", False, "超时未获取session_id")
                        break

                except json.JSONDecodeError:
                    logger.warning(f"无法解析SSE数据: {event.data}")
                except Exception as e:
                    logger.error(f"处理SSE事件时出错: {e}")

            return session_id

        except requests.exceptions.Timeout:
            self.add_result("sse_connection", False, "连接超时")
            return None
        except Exception as e:
            self.add_result("sse_connection", False, f"连接异常: {str(e)}")
            return None

    def test_tools_list(self, session_id: str) -> bool:
        """测试tools/list方法"""
        if not session_id:
            self.add_result("tools_list", False, "缺少session_id")
            return False

        url = f"{self.base_url}/sse/messages/?session_id={session_id}"
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }

        try:
            logger.info("测试tools/list方法...")
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if "result" in data and "tools" in data["result"]:
                    tools = data["result"]["tools"]
                    tool_names = [tool.get("name", "unknown") for tool in tools]
                    self.add_result("tools_list", True, f"成功获取工具列表: {tool_names}", session_id)
                    return True
                else:
                    self.add_result("tools_list", False, f"响应格式错误: {data}", session_id)
            else:
                self.add_result("tools_list", False, f"HTTP错误: {response.status_code}", session_id)

        except Exception as e:
            self.add_result("tools_list", False, f"请求异常: {str(e)}", session_id)

        return False

    def test_tools_call(self, session_id: str) -> bool:
        """测试tools/call方法"""
        if not session_id:
            self.add_result("tools_call", False, "缺少session_id")
            return False

        url = f"{self.base_url}/sse/messages/?session_id={session_id}"
        payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "greet_user",
                "arguments": {"name": "MCP测试用户"}
            }
        }

        try:
            logger.info("测试tools/call方法...")
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    result = data["result"]
                    self.add_result("tools_call", True, f"成功调用工具，结果: {result}", session_id)
                    return True
                else:
                    self.add_result("tools_call", False, f"响应格式错误: {data}", session_id)
            else:
                self.add_result("tools_call", False, f"HTTP错误: {response.status_code}", session_id)

        except Exception as e:
            self.add_result("tools_call", False, f"请求异常: {str(e)}", session_id)

        return False

    def test_unauthorized_access(self):
        """测试未授权访问"""
        # 测试无token的SSE连接
        sse_url = f"{self.base_url}/sse"
        try:
            response = requests.get(sse_url, timeout=5)
            passed = response.status_code == 401
            self.add_result("sse_unauthorized", passed,
                          f"无token访问SSE: {response.status_code}" + ("✅" if passed else "❌"))
        except Exception as e:
            self.add_result("sse_unauthorized", False, f"异常: {str(e)}")

        # 测试无token的消息发送
        url = f"{self.base_url}/sse/messages/?session_id=test"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
        try:
            response = requests.post(url, json=payload, timeout=5)
            passed = response.status_code == 401
            self.add_result("messages_unauthorized", passed,
                          f"无token发送消息: {response.status_code}" + ("✅" if passed else "❌"))
        except Exception as e:
            self.add_result("messages_unauthorized", False, f"异常: {str(e)}")

    def run_all_tests(self):
        """运行所有MCP测试"""
        logger.info("=== MCP SSE 协议测试开始 ===")

        # 测试未授权访问
        self.test_unauthorized_access()

        # 测试SSE连接和工具调用
        session_id = self.test_sse_connection()

        if session_id:
            # 测试工具列表
            self.test_tools_list(session_id)

            # 测试工具调用
            self.test_tools_call(session_id)
        else:
            logger.error("无法获取session_id，跳过工具测试")

    def generate_report(self) -> str:
        """生成MCP测试报告"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["passed"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        report = f"""
# MCP SSE 协议测试报告

**测试时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}
**测试目标**: {self.base_url}
**Token**: {self.token[:20]}...

## 测试结果概览
- 总测试数: {total_tests}
- 通过测试: {passed_tests}
- 失败测试: {total_tests - passed_tests}
- 成功率: {success_rate:.1f}%

## 详细测试结果

"""

        for result in self.results:
            status = "✅ 通过" if result["passed"] else "❌ 失败"
            report += f"### {result['test_name']}\n"
            report += f"- **状态**: {status}\n"
            report += f"- **详情**: {result['details']}\n"
            if result["session_id"]:
                report += f"- **会话ID**: {result['session_id']}\n"
            report += f"- **测试时间**: {result['timestamp']}\n\n"

        # MCP功能评估
        sse_ok = any(r["passed"] for r in self.results if "sse_connection" in r["test_name"])
        tools_ok = any(r["passed"] for r in self.results if "tools_list" in r["test_name"])
        call_ok = any(r["passed"] for r in self.results if "tools_call" in r["test_name"])
        auth_ok = any(r["passed"] for r in self.results if "unauthorized" in r["test_name"])

        report += f"""
## MCP功能评估
- **SSE连接**: {'✅ 正常' if sse_ok else '❌ 异常'}
- **工具发现**: {'✅ 正常' if tools_ok else '❌ 异常'}
- **工具调用**: {'✅ 正常' if call_ok else '❌ 异常'}
- **认证保护**: {'✅ 正常' if auth_ok else '❌ 异常'}
"""

        return report

def main():
    """主测试函数"""
    print("🔗 开始 MCP SSE 协议测试")

    if not SSE_AVAILABLE:
        print("⚠️  警告: SSEClient库未安装，SSE测试将被跳过")
        print("安装命令: pip install sseclient-py")

    test_suite = MCPTestSuite()

    try:
        test_suite.run_all_tests()
        report = test_suite.generate_report()

        # 保存报告
        with open("mcp_test_report.md", "w", encoding="utf-8") as f:
            f.write(report)

        print("\n" + "="*60)
        print("📊 MCP测试完成！详细报告已保存到 mcp_test_report.md")
        print("="*60)

        # 显示关键结果
        total_tests = len(test_suite.results)
        passed_tests = sum(1 for r in test_suite.results if r["passed"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print(f"📈 成功率: {success_rate:.1f}% ({passed_tests}/{total_tests})")

        if success_rate >= 80:
            print("🎉 MCP功能基本正常！")
        else:
            print("⚠️  MCP功能存在问题，请查看详细报告。")

    except KeyboardInterrupt:
        print("\n❌ 测试被用户中断")
    except Exception as e:
        print(f"❌ 测试执行失败: {str(e)}")

if __name__ == "__main__":
    main()