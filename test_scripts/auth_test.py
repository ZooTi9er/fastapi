#!/usr/bin/env python3
"""
FastAPI MCP SSE 服务认证功能测试脚本
"""
import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FastAPITestSuite:
    def __init__(self, base_url: str = "http://localhost:1234", token: str = "sk-wuzhe12345"):
        self.base_url = base_url
        self.token = token
        self.results = []

    def add_result(self, test_name: str, passed: bool, details: str = "", response_time: float = 0):
        """添加测试结果"""
        self.results.append({
            "test_name": test_name,
            "passed": passed,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        })

    def get_headers(self, with_token: bool = True) -> Dict[str, str]:
        """获取请求头"""
        if with_token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    def test_endpoint(self, method: str, endpoint: str, with_token: bool = True,
                     data: Optional[Dict] = None, expected_status: int = 200) -> bool:
        """测试单个端点"""
        url = f"{self.base_url}{endpoint}"
        headers = self.get_headers(with_token)

        try:
            start_time = time.time()
            response = requests.request(method, url, headers=headers, json=data, timeout=10)
            response_time = time.time() - start_time

            passed = response.status_code == expected_status
            details = f"状态码: {response.status_code}, 期望: {expected_status}"

            if passed:
                logger.info(f"✅ {method} {endpoint} - {details}")
            else:
                logger.error(f"❌ {method} {endpoint} - {details}")
                if response.text:
                    details += f", 响应: {response.text[:200]}"

            self.add_result(f"{method}_{endpoint.replace('/', '_')}", passed, details, response_time)
            return passed

        except requests.exceptions.Timeout:
            logger.error(f"❌ {method} {endpoint} - 请求超时")
            self.add_result(f"{method}_{endpoint.replace('/', '_')}", False, "请求超时", 10)
            return False
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ {method} {endpoint} - 连接错误")
            self.add_result(f"{method}_{endpoint.replace('/', '_')}", False, "连接错误", 0)
            return False
        except Exception as e:
            logger.error(f"❌ {method} {endpoint} - 异常: {str(e)}")
            self.add_result(f"{method}_{endpoint.replace('/', '_')}", False, f"异常: {str(e)}", 0)
            return False

    def run_basic_connectivity_tests(self):
        """基础连接测试"""
        logger.info("=== 基础连接测试 ===")

        # 测试健康检查（应该公开访问）
        self.test_endpoint("GET", "/health", with_token=False, expected_status=200)

        # 测试根路径无认证（应该失败）
        self.test_endpoint("GET", "/", with_token=False, expected_status=401)

        # 测试根路径有认证（应该成功）
        self.test_endpoint("GET", "/", with_token=True, expected_status=200)

        # 测试hello端点无认证（应该失败）
        self.test_endpoint("GET", "/hello/test", with_token=False, expected_status=401)

        # 测试hello端点有认证（应该成功）
        self.test_endpoint("GET", "/hello/test", with_token=True, expected_status=200)

    def run_authentication_tests(self):
        """认证功能测试"""
        logger.info("=== 认证功能测试 ===")

        # 测试错误token
        old_token = self.token
        self.token = "wrong_token"
        self.test_endpoint("GET", "/", with_token=True, expected_status=401)
        self.token = old_token

        # 测试无Authorization头
        self.test_endpoint("GET", "/", with_token=False, expected_status=401)

        # 测试正确token
        self.test_endpoint("GET", "/", with_token=True, expected_status=200)

        # 测试token格式（缺少Bearer）
        url = f"{self.base_url}/"
        try:
            response = requests.get(url, headers={"Authorization": self.token}, timeout=10)
            passed = response.status_code == 401
            details = f"状态码: {response.status_code} (期望401)"
            logger.info(f"{'✅' if passed else '❌'} Token格式测试 - {details}")
            self.add_result("token_format_test", passed, details)
        except Exception as e:
            logger.error(f"❌ Token格式测试 - 异常: {str(e)}")
            self.add_result("token_format_test", False, f"异常: {str(e)}")

    def run_sse_tests(self):
        """SSE连接测试"""
        logger.info("=== SSE连接测试 ===")

        # 测试SSE连接无认证
        url = f"{self.base_url}/sse"
        try:
            response = requests.get(url, timeout=5)
            passed = response.status_code == 401
            details = f"SSE无认证连接 - 状态码: {response.status_code}"
            logger.info(f"{'✅' if passed else '❌'} {details}")
            self.add_result("sse_no_auth", passed, details)
        except Exception as e:
            logger.error(f"❌ SSE无认证测试 - 异常: {str(e)}")
            self.add_result("sse_no_auth", False, f"异常: {str(e)}")

        # 测试SSE连接有认证
        try:
            headers = self.get_headers(True)
            response = requests.get(url, headers=headers, timeout=5)
            passed = response.status_code == 200
            details = f"SSE有认证连接 - 状态码: {response.status_code}"
            logger.info(f"{'✅' if passed else '❌'} {details}")
            self.add_result("sse_with_auth", passed, details)
        except Exception as e:
            logger.error(f"❌ SSE有认证测试 - 异常: {str(e)}")
            self.add_result("sse_with_auth", False, f"异常: {str(e)}")

    def run_performance_tests(self):
        """性能测试"""
        logger.info("=== 性能测试 ===")

        # 测试响应时间
        endpoints = ["/health", "/", "/hello/performance_test"]
        for endpoint in endpoints:
            if endpoint == "/health":
                # 健康检查应该快速响应
                self.test_endpoint("GET", endpoint, with_token=False, expected_status=200)
            else:
                self.test_endpoint("GET", endpoint, with_token=True, expected_status=200)

    def generate_report(self) -> str:
        """生成测试报告"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["passed"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        report = f"""
# FastAPI MCP SSE 服务认证测试报告

**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
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
            if result["response_time"] > 0:
                report += f"- **响应时间**: {result['response_time']:.3f}s\n"
            report += f"- **测试时间**: {result['timestamp']}\n\n"

        # 性能分析
        response_times = [r["response_time"] for r in self.results if r["response_time"] > 0]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)

            report += f"""
## 性能分析
- 平均响应时间: {avg_time:.3f}s
- 最大响应时间: {max_time:.3f}s
- 最小响应时间: {min_time:.3f}s
"""

        # 安全评估
        auth_passed = all(r["passed"] for r in self.results if "auth" in r["test_name"].lower())
        health_public = any(r["passed"] for r in self.results if "health" in r["test_name"].lower())
        endpoints_protected = any(r["passed"] for r in self.results if "_" in r["test_name"] and r["test_name"] not in ["GET_health"])

        report += f"""
## 安全评估
- **认证机制**: {'✅ 正常' if auth_passed else '❌ 异常'}
- **健康检查**: {'✅ 公开访问' if health_public else '❌ 应公开但被保护'}
- **端点保护**: {'✅ 正常' if endpoints_protected else '❌ 保护异常'}
"""

        # 建议
        if success_rate < 100:
            failed_tests = [r for r in self.results if not r["passed"]]
            report += """
## 建议和改进
"""
            for test in failed_tests:
                report += f"- 修复 {test['test_name']}: {test['details']}\n"
        else:
            report += """
## 总结
✅ 所有测试通过，认证功能工作正常。
"""

        return report

def main():
    """主测试函数"""
    print("🚀 开始 FastAPI MCP SSE 服务认证测试")

    # 创建测试套件
    test_suite = FastAPITestSuite()

    try:
        # 运行测试
        test_suite.run_basic_connectivity_tests()
        test_suite.run_authentication_tests()
        test_suite.run_sse_tests()
        test_suite.run_performance_tests()

        # 生成报告
        report = test_suite.generate_report()

        # 保存报告
        with open("test_report.md", "w", encoding="utf-8") as f:
            f.write(report)

        print("\n" + "="*60)
        print("📊 测试完成！详细报告已保存到 test_report.md")
        print("="*60)

        # 显示关键结果
        total_tests = len(test_suite.results)
        passed_tests = sum(1 for r in test_suite.results if r["passed"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print(f"📈 成功率: {success_rate:.1f}% ({passed_tests}/{total_tests})")

        if success_rate == 100:
            print("🎉 所有测试通过！认证功能工作正常。")
        else:
            print("⚠️  部分测试失败，请查看详细报告。")

    except KeyboardInterrupt:
        print("\n❌ 测试被用户中断")
    except Exception as e:
        print(f"❌ 测试执行失败: {str(e)}")

if __name__ == "__main__":
    main()