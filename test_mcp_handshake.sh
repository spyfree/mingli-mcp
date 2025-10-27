#!/bin/bash
# MCP握手测试脚本

set -e

echo "🧪 测试MCP stdio模式握手"
echo "======================================"

cd "$(dirname "$0")"
source venv/bin/activate

export TRANSPORT_TYPE=stdio
export LOG_LEVEL=ERROR  # 减少日志输出

echo ""
echo "📋 测试1: Initialize"
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | python mingli_mcp.py 2>/dev/null | python -m json.tool

echo ""
echo "📋 测试2: 完整握手流程"
{
  echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
  echo '{"jsonrpc":"2.0","method":"notifications/initialized"}'
  echo '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
} | python mingli_mcp.py 2>/dev/null

echo ""
echo "✅ 测试完成！"
