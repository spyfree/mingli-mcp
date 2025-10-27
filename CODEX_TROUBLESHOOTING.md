# Codex MCP 问题排查指南

## 🔍 问题1：握手失败 (handshaking failed)

### 错误信息
\`\`\`
MCP client for 'mingli' failed to start: handshaking with MCP server failed: 
connection closed: initialize response
\`\`\`

### 原因分析

这个错误通常是因为：
1. **日志输出干扰了stdio通信** - 日志输出到stdout而不是stderr
2. **JSON格式问题** - 响应格式不符合MCP协议
3. **启动错误** - 服务启动过程中有错误

---

## ✅ 解决方案

### 方案1：使用最新代码（已修复）

最新版本已经修复了日志输出问题。

\`\`\`bash
cd /Users/lix18854/Documents/code/ziwei_mcp
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
\`\`\`

然后配置Codex：

\`\`\`toml
[mcp_servers.mingli]
command = "/Users/lix18854/Documents/code/ziwei_mcp/venv/bin/python"
args = ["/Users/lix18854/Documents/code/ziwei_mcp/mingli_mcp.py"]
startup_timeout_sec = 15

[mcp_servers.mingli.env]
TRANSPORT_TYPE = "stdio"
LOG_LEVEL = "ERROR"  # 减少日志输出
\`\`\`

---

### 方案2：使用PyPI包（推荐）

PyPI包已经过测试，更稳定。

#### 步骤1：安装包

\`\`\`bash
# 使用pipx（推荐）
pipx install mingli-mcp

# 或使用pip
pip install --user mingli-mcp
\`\`\`

#### 步骤2：配置Codex

\`\`\`toml
[mcp_servers.mingli]
command = "mingli-mcp"
startup_timeout_sec = 20

[mcp_servers.mingli.env]
TRANSPORT_TYPE = "stdio"
LOG_LEVEL = "ERROR"
\`\`\`

---

### 方案3：创建包装脚本

创建一个干净的启动脚本，确保日志不干扰输出。

#### 创建脚本

\`\`\`bash
nano ~/.local/bin/mingli-mcp-wrapper.sh
\`\`\`

**内容**：

\`\`\`bash
#!/bin/bash
cd /Users/lix18854/Documents/code/ziwei_mcp
source venv/bin/activate
export TRANSPORT_TYPE=stdio
export LOG_LEVEL=ERROR
exec python mingli_mcp.py 2>/dev/null  # 重定向stderr到/dev/null
\`\`\`

\`\`\`bash
chmod +x ~/.local/bin/mingli-mcp-wrapper.sh
\`\`\`

#### 配置Codex

\`\`\`toml
[mcp_servers.mingli]
command = "/Users/lix18854/.local/bin/mingli-mcp-wrapper.sh"
startup_timeout_sec = 15
\`\`\`

---

## 🧪 测试MCP握手

### 手动测试

\`\`\`bash
cd /Users/lix18854/Documents/code/ziwei_mcp
source venv/bin/activate

# 测试initialize
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | \\
  TRANSPORT_TYPE=stdio LOG_LEVEL=ERROR python mingli_mcp.py 2>/dev/null
\`\`\`

**预期输出**（单行JSON）：
\`\`\`json
{"jsonrpc": "2.0", "result": {"protocolVersion": "2024-11-05", "serverInfo": {"name": "ziwei_mcp", "version": "1.0.0"}, "capabilities": {"tools": {}}}, "id": 1}
\`\`\`

### 使用测试脚本

\`\`\`bash
./test_mcp_handshake.sh
\`\`\`

---

## 🐛 调试步骤

### 步骤1：检查命令是否可执行

\`\`\`bash
# 测试命令
which mingli-mcp

# 或测试本地路径
/Users/lix18854/Documents/code/ziwei_mcp/venv/bin/python \\
  /Users/lix18854/Documents/code/ziwei_mcp/mingli_mcp.py --help
\`\`\`

### 步骤2：查看stderr输出

\`\`\`bash
# 看看是否有错误
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | \\
  TRANSPORT_TYPE=stdio python mingli_mcp.py 2>&1 | head -20
\`\`\`

### 步骤3：测试完整流程

\`\`\`bash
{
  echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
  sleep 1
  echo '{"jsonrpc":"2.0","method":"notifications/initialized"}'
  sleep 1
  echo '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
  sleep 1
} | TRANSPORT_TYPE=stdio LOG_LEVEL=ERROR python mingli_mcp.py 2>/dev/null
\`\`\`

### 步骤4：检查Codex日志

Codex可能有日志文件，查看详细错误：

\`\`\`bash
# 可能的日志位置
tail -f ~/.codex/logs/*.log
# 或
tail -f ~/.config/codex/logs/*.log
\`\`\`

---

## 📝 配置检查清单

### ✅ 确认项

- [ ] config.toml路径正确：\`~/.codex/config.toml\`
- [ ] command路径正确（使用\`which\`验证）
- [ ] startup_timeout_sec >= 20秒
- [ ] 环境变量设置：TRANSPORT_TYPE=stdio, LOG_LEVEL=ERROR
- [ ] Python环境可用（虚拟环境已激活或使用完整路径）

### 示例配置

\`\`\`toml
# ~/.codex/config.toml

# 推荐配置（本地路径）
[mcp_servers.mingli]
command = "/Users/lix18854/Documents/code/ziwei_mcp/venv/bin/python"
args = ["/Users/lix18854/Documents/code/ziwei_mcp/mingli_mcp.py"]
startup_timeout_sec = 15

[mcp_servers.mingli.env]
TRANSPORT_TYPE = "stdio"
LOG_LEVEL = "ERROR"
\`\`\`

---

## 🔧 常见问题

### Q1: 输出有乱码或额外信息

**A**: 确保LOG_LEVEL=ERROR，减少日志输出

\`\`\`toml
[mcp_servers.mingli.env]
LOG_LEVEL = "ERROR"  # 或 "CRITICAL"
\`\`\`

### Q2: Permission denied

**A**: 检查文件权限

\`\`\`bash
chmod +x /Users/lix18854/Documents/code/ziwei_mcp/mingli_mcp.py
chmod +x /Users/lix18854/Documents/code/ziwei_mcp/venv/bin/python
\`\`\`

### Q3: 依赖缺失

**A**: 重新安装依赖

\`\`\`bash
cd /Users/lix18854/Documents/code/ziwei_mcp
source venv/bin/activate
pip install -r requirements.txt
\`\`\`

### Q4: 还是不行

**A**: 尝试HTTP模式（使用Cloudflare Tunnel）

虽然Codex可能主要支持stdio，但如果实在不行，可以：

1. 启动HTTP服务 + Cloudflare Tunnel
2. 看Codex是否支持HTTP端点配置

---

## 💡 推荐配置（三选一）

### 选项1：本地路径（最稳定）⭐⭐⭐⭐⭐

\`\`\`toml
[mcp_servers.mingli]
command = "/Users/lix18854/Documents/code/ziwei_mcp/venv/bin/python"
args = ["/Users/lix18854/Documents/code/ziwei_mcp/mingli_mcp.py"]
startup_timeout_sec = 15
[mcp_servers.mingli.env]
TRANSPORT_TYPE = "stdio"
LOG_LEVEL = "ERROR"
\`\`\`

### 选项2：pipx安装

\`\`\`bash
pipx install mingli-mcp
\`\`\`

\`\`\`toml
[mcp_servers.mingli]
command = "mingli-mcp"
startup_timeout_sec = 20
[mcp_servers.mingli.env]
TRANSPORT_TYPE = "stdio"
LOG_LEVEL = "ERROR"
\`\`\`

### 选项3：包装脚本

\`\`\`toml
[mcp_servers.mingli]
command = "/Users/lix18854/.local/bin/mingli-mcp-wrapper.sh"
startup_timeout_sec = 15
\`\`\`

---

## 📞 还需要帮助？

1. **运行测试脚本**：\`./test_mcp_handshake.sh\`
2. **查看详细日志**：移除\`2>/dev/null\`查看错误
3. **检查Codex版本**：确保使用最新版
4. **GitHub Issue**：如果问题持续，在项目创建issue

---

**最快解决方案**：使用选项1（本地路径配置）+ LOG_LEVEL=ERROR
