
# FastAPI MCP SSE 服务认证测试报告

**测试时间**: 2025-09-17 19:59:31
**测试目标**: http://mini.ewuzhe.dpdns.org:1234
**Token**: sk-wuzhe12345...

## 测试结果概览
- 总测试数: 14
- 通过测试: 0
- 失败测试: 14
- 成功率: 0.0%

## 详细测试结果

### GET__health
- **状态**: ❌ 失败
- **详情**: 连接错误
- **测试时间**: 2025-09-17T19:59:31.301677

### GET__
- **状态**: ❌ 失败
- **详情**: 连接错误
- **测试时间**: 2025-09-17T19:59:31.302264

### GET__
- **状态**: ❌ 失败
- **详情**: 连接错误
- **测试时间**: 2025-09-17T19:59:31.302735

### GET__hello_test
- **状态**: ❌ 失败
- **详情**: 连接错误
- **测试时间**: 2025-09-17T19:59:31.303184

### GET__hello_test
- **状态**: ❌ 失败
- **详情**: 连接错误
- **测试时间**: 2025-09-17T19:59:31.303669

### GET__
- **状态**: ❌ 失败
- **详情**: 连接错误
- **测试时间**: 2025-09-17T19:59:31.304294

### GET__
- **状态**: ❌ 失败
- **详情**: 连接错误
- **测试时间**: 2025-09-17T19:59:31.304746

### GET__
- **状态**: ❌ 失败
- **详情**: 连接错误
- **测试时间**: 2025-09-17T19:59:31.305238

### token_format_test
- **状态**: ❌ 失败
- **详情**: 异常: HTTPConnectionPool(host='127.0.0.1', port=10808): Max retries exceeded with url: http://mini.ewuzhe.dpdns.org:1234/ (Caused by ProxyError('Unable to connect to proxy', NewConnectionError('<urllib3.connection.HTTPConnection object at 0x103fcd9a0>: Failed to establish a new connection: [Errno 61] Connection refused')))
- **测试时间**: 2025-09-17T19:59:31.305710

### sse_no_auth
- **状态**: ❌ 失败
- **详情**: 异常: HTTPConnectionPool(host='127.0.0.1', port=10808): Max retries exceeded with url: http://mini.ewuzhe.dpdns.org:1234/sse (Caused by ProxyError('Unable to connect to proxy', NewConnectionError('<urllib3.connection.HTTPConnection object at 0x103fce450>: Failed to establish a new connection: [Errno 61] Connection refused')))
- **测试时间**: 2025-09-17T19:59:31.306193

### sse_with_auth
- **状态**: ❌ 失败
- **详情**: 异常: HTTPConnectionPool(host='127.0.0.1', port=10808): Max retries exceeded with url: http://mini.ewuzhe.dpdns.org:1234/sse (Caused by ProxyError('Unable to connect to proxy', NewConnectionError('<urllib3.connection.HTTPConnection object at 0x103f97dd0>: Failed to establish a new connection: [Errno 61] Connection refused')))
- **测试时间**: 2025-09-17T19:59:31.306825

### GET__health
- **状态**: ❌ 失败
- **详情**: 连接错误
- **测试时间**: 2025-09-17T19:59:31.307282

### GET__
- **状态**: ❌ 失败
- **详情**: 连接错误
- **测试时间**: 2025-09-17T19:59:31.307690

### GET__hello_performance_test
- **状态**: ❌ 失败
- **详情**: 连接错误
- **测试时间**: 2025-09-17T19:59:31.308107


## 安全评估
- **认证机制**: ❌ 异常
- **健康检查**: ❌ 应公开但被保护
- **端点保护**: ❌ 保护异常

## 建议和改进
- 修复 GET__health: 连接错误
- 修复 GET__: 连接错误
- 修复 GET__: 连接错误
- 修复 GET__hello_test: 连接错误
- 修复 GET__hello_test: 连接错误
- 修复 GET__: 连接错误
- 修复 GET__: 连接错误
- 修复 GET__: 连接错误
- 修复 token_format_test: 异常: HTTPConnectionPool(host='127.0.0.1', port=10808): Max retries exceeded with url: http://mini.ewuzhe.dpdns.org:1234/ (Caused by ProxyError('Unable to connect to proxy', NewConnectionError('<urllib3.connection.HTTPConnection object at 0x103fcd9a0>: Failed to establish a new connection: [Errno 61] Connection refused')))
- 修复 sse_no_auth: 异常: HTTPConnectionPool(host='127.0.0.1', port=10808): Max retries exceeded with url: http://mini.ewuzhe.dpdns.org:1234/sse (Caused by ProxyError('Unable to connect to proxy', NewConnectionError('<urllib3.connection.HTTPConnection object at 0x103fce450>: Failed to establish a new connection: [Errno 61] Connection refused')))
- 修复 sse_with_auth: 异常: HTTPConnectionPool(host='127.0.0.1', port=10808): Max retries exceeded with url: http://mini.ewuzhe.dpdns.org:1234/sse (Caused by ProxyError('Unable to connect to proxy', NewConnectionError('<urllib3.connection.HTTPConnection object at 0x103f97dd0>: Failed to establish a new connection: [Errno 61] Connection refused')))
- 修复 GET__health: 连接错误
- 修复 GET__: 连接错误
- 修复 GET__hello_performance_test: 连接错误
