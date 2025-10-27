# Codex MCP 快速修复指南

## 🎯 问题

\`\`\`
MCP client for 'mingli' failed to start: handshaking with MCP server failed: 
connection closed: initialize response
\`\`\`

## ✅ 已修复！

最新代码已经修复了日志输出问题。

---

## 🚀 快速解决（选一个）

### 方案1：使用本地最新代码（推荐）⭐⭐⭐⭐⭐

#### 步骤1：更新代码

\`\`\`bash
cd /Users/lix18854/Documents/code/ziwei_mcp
git pull origin main
\`\`\`

#### 步骤2：配置Codex

编辑 \`~/.codex/config.toml\`：

\`\`\`toml
[mcp_servers.mingli]
command = "/Users/lix18854/Documents/code/ziwei_mcp/venv/bin/python"
args = ["/Users/lix18854/Documents/code/ziwei_mcp/mingli_mcp.py"]
startup_timeout_sec = 15

[mcp_servers.mingli.env]
TRANSPORT_TYPE = "stdio"
LOG_LEVEL = "ERROR"
\`\`\`

#### 步骤3：重启Codex

完全退出并重新打开Codex。

---

### 方案2：重新安装PyPI包（等v1.0.2发布）

如果你不想用本地代码，等我发布v1.0.2到PyPI后：

\`\`\`bash
pipx install --force mingli-mcp==1.0.2
\`\`\`

\`\`\`toml
[mcp_servers.mingli]
command = "mingli-mcp"
startup_timeout_sec = 20

[mcp_servers.mingli.env]
TRANSPORT_TYPE = "stdio"
LOG_LEVEL = "ERROR"
\`\`\`

---

## 🧪 测试是否修复

### 测试1：手动测试MCP握手

\`\`\`bash
cd /Users/lix18854/Documents/code/ziwei_mcp
source venv/bin/activate

echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | \\
  TRANSPORT_TYPE=stdio LOG_LEVEL=ERROR python mingli_mcp.py 2>/dev/null
\`\`\`

**预期输出**（单行JSON，无其他输出）：
\`\`\`json
{"jsonrpc": "2.0", "result": {"protocolVersion": "2024-11-05", "serverInfo": {"name": "ziwei_mcp", "version": "1.0.0"}, "capabilities": {"tools": {}}}, "id": 1}
\`\`\`

### 测试2：使用测试脚本

\`\`\`bash
cd /Users/lix18854/Documents/code/ziwei_mcp
./test_mcp_handshake.sh
\`\`\`

---

## 📝 完整配置示例

### ~/.codex/config.toml

\`\`\`toml
# 命理MCP服务配置
[mcp_servers.mingli]
command = "/Users/lix18854/Documents/code/ziwei_mcp/venv/bin/python"
args = ["/Users/lix18854/Documents/code/ziwei_mcp/mingli_mcp.py"]
startup_timeout_sec = 15

[mcp_servers.mingli.env]
TRANSPORT_TYPE = "stdio"
LOG_LEVEL = "ERROR"  # 只输出错误，避免干扰通信
\`\`\`

---

## 🎯 关键修复点

### 之前的问题

日志配置使用 \`logging.StreamHandler()\`，默认输出可能干扰stdio通信。

### 修复方案

在stdio模式下，明确指定日志输出到stderr：

\`\`\`python
if TRANSPORT_TYPE == 'stdio':
    logging.basicConfig(
        handlers=[
            logging.StreamHandler(sys.stderr)  # 明确输出到stderr
        ]
    )
\`\`\`

---

## 🎉 测试MCP功能

配置并重启Codex后，尝试：

\`\`\`
列出所有可用的命理系统
\`\`\`

或

\`\`\`
帮我排个紫微斗数盘：2000年8月16日寅时女性
\`\`\`

---

## 🐛 如果还有问题

### 调试步骤

1. **查看stderr输出**
   \`\`\`bash
   echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | \\
     TRANSPORT_TYPE=stdio python mingli_mcp.py 2>&1
   \`\`\`

2. **检查配置**
   \`\`\`bash
   cat ~/.codex/config.toml
   \`\`\`

3. **验证命令可用**
   \`\`\`bash
   /Users/lix18854/Documents/code/ziwei_mcp/venv/bin/python \\
     /Users/lix18854/Documents/code/ziwei_mcp/mingli_mcp.py --help
   \`\`\`

4. **查看详细文档**
   查看 \`CODEX_TROUBLESHOOTING.md\` 获取更多调试方法

---

## 📞 需要发布v1.0.2吗？

如果你想让PyPI用户也能使用修复后的版本，我可以帮你：

1. 更新版本号到1.0.2
2. 构建并上传到PyPI
3. 你就可以用 \`pipx install mingli-mcp\` 了

要我现在帮你发布吗？
