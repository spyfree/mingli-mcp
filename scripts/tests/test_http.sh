#!/bin/bash
# 测试HTTP MCP服务

echo "=== 测试HTTP MCP服务 ==="

# 设置环境变量
export TRANSPORT_TYPE=http
export HTTP_PORT=8080
export LOG_LEVEL=INFO

# 启动服务（后台运行）
echo "启动HTTP服务..."
python mingli_mcp.py &
SERVER_PID=$!

# 等待服务启动
sleep 3

# 测试健康检查
echo -e "\n测试健康检查端点..."
curl -s http://localhost:8080/health | python -m json.tool

# 测试根路径
echo -e "\n测试根路径..."
curl -s http://localhost:8080/ | python -m json.tool

# 测试MCP请求
echo -e "\n测试MCP初始化请求..."
curl -s -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "clientInfo": {
        "name": "test-client",
        "version": "1.0.0"
      }
    }
  }' | python -m json.tool

# 测试工具列表
echo -e "\n测试工具列表..."
curl -s -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }' | python -m json.tool | head -50

# 停止服务
echo -e "\n停止HTTP服务..."
kill $SERVER_PID

echo -e "\n=== 测试完成 ==="
