# 升级指南

## 🎉 v1.0.2 已发布到PyPI！

**发布时间**：2025-10-27  
**PyPI链接**：https://pypi.org/project/mingli-mcp/1.0.2/

### 主要修复

- ✅ 修复stdio模式日志输出问题
- ✅ 解决MCP握手失败（handshaking failed）
- ✅ 日志明确输出到stderr，不干扰stdout通信
- ✅ 提升Codex等MCP客户端的兼容性

---

## 🚀 如何升级

### 方式1：使用pipx（推荐）

如果你之前用pipx安装：

\`\`\`bash
# 升级到最新版本
pipx upgrade mingli-mcp

# 验证版本
mingli-mcp --version
# 或
pipx list | grep mingli-mcp
\`\`\`

### 方式2：使用pip

如果你用pip安装：

\`\`\`bash
# 升级
pip install --upgrade mingli-mcp

# 验证
pip show mingli-mcp | grep Version
\`\`\`

### 方式3：强制重装（如果升级有问题）

\`\`\`bash
# pipx方式
pipx uninstall mingli-mcp
pipx install mingli-mcp

# pip方式
pip uninstall mingli-mcp
pip install mingli-mcp
\`\`\`

### 方式4：使用uvx（自动使用最新版本）

uvx会自动使用最新版本，无需手动升级：

\`\`\`bash
# 直接使用即可，uvx会自动获取最新版
uvx mingli-mcp@latest --help
\`\`\`

---

## 📝 Codex配置更新

### 如果使用pipx/pip安装

\`\`\`toml
# ~/.codex/config.toml

[mcp_servers.mingli]
command = "mingli-mcp"
startup_timeout_sec = 20

[mcp_servers.mingli.env]
TRANSPORT_TYPE = "stdio"
LOG_LEVEL = "ERROR"
\`\`\`

升级后**重启Codex**即可。

### 如果使用uvx

\`\`\`toml
# ~/.codex/config.toml

[mcp_servers.mingli]
command = "uvx"
args = ["mingli-mcp@latest"]  # 或 ["mingli-mcp@1.0.2"]
startup_timeout_sec = 60

[mcp_servers.mingli.env]
TRANSPORT_TYPE = "stdio"
LOG_LEVEL = "ERROR"
\`\`\`

### 如果使用本地路径

\`\`\`bash
# 拉取最新代码
cd /Users/lix18854/Documents/code/ziwei_mcp
git pull origin main
\`\`\`

配置不变：

\`\`\`toml
[mcp_servers.mingli]
command = "/Users/lix18854/Documents/code/ziwei_mcp/venv/bin/python"
args = ["/Users/lix18854/Documents/code/ziwei_mcp/mingli_mcp.py"]
startup_timeout_sec = 15

[mcp_servers.mingli.env]
TRANSPORT_TYPE = "stdio"
LOG_LEVEL = "ERROR"
\`\`\`

---

## 🧪 验证升级

### 步骤1：检查版本

\`\`\`bash
# pipx
pipx list | grep mingli-mcp

# pip
pip show mingli-mcp

# uvx
uvx mingli-mcp@latest --version
\`\`\`

应该显示 **1.0.2** 或更新。

### 步骤2：测试MCP握手

\`\`\`bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | \\
  mingli-mcp 2>/dev/null
\`\`\`

**预期输出**（干净的JSON）：
\`\`\`json
{"jsonrpc": "2.0", "result": {"protocolVersion": "2024-11-05", "serverInfo": {"name": "ziwei_mcp", "version": "1.0.0"}, "capabilities": {"tools": {}}}, "id": 1}
\`\`\`

### 步骤3：在Codex中测试

重启Codex后，尝试：

\`\`\`
列出所有命理系统
\`\`\`

应该正常返回结果，不再有握手错误。

---

## 🔄 版本历史

| 版本 | 发布日期 | 主要变更 |
|------|---------|---------|
| **1.0.2** | 2025-10-27 | 修复stdio日志输出，解决握手失败 |
| 1.0.1 | 2025-10-27 | 修复PyPI包配置 |
| 1.0.0 | 2025-10-27 | 初始发布 |

---

## 🐛 如果升级后还有问题

### 清除缓存

\`\`\`bash
# pip缓存
pip cache purge

# pipx重装
pipx uninstall mingli-mcp
pipx install mingli-mcp --force

# uvx清除缓存
rm -rf ~/.cache/uv
\`\`\`

### 验证安装

\`\`\`bash
# 找到安装位置
which mingli-mcp

# 查看详细信息
pip show mingli-mcp

# 测试运行
mingli-mcp --help
\`\`\`

### 查看日志

在Codex配置中临时启用详细日志：

\`\`\`toml
[mcp_servers.mingli.env]
LOG_LEVEL = "DEBUG"
\`\`\`

然后查看Codex日志文件。

---

## 📞 需要帮助？

1. **查看文档**
   - \`CODEX_CONFIG.md\` - Codex配置指南
   - \`CODEX_TROUBLESHOOTING.md\` - 问题排查
   - \`QUICK_FIX_CODEX.md\` - 快速修复

2. **GitHub Issues**
   - 项目地址：https://github.com/spyfree/mingli-mcp
   - 创建Issue描述问题

3. **查看PyPI**
   - 包页面：https://pypi.org/project/mingli-mcp/
   - 发布历史：https://pypi.org/project/mingli-mcp/#history

---

## 🎯 推荐配置

### 开发者（需要频繁修改代码）

使用本地路径，代码修改立即生效：

\`\`\`toml
[mcp_servers.mingli]
command = "/Users/lix18854/Documents/code/ziwei_mcp/venv/bin/python"
args = ["/Users/lix18854/Documents/code/ziwei_mcp/mingli_mcp.py"]
startup_timeout_sec = 15
[mcp_servers.mingli.env]
TRANSPORT_TYPE = "stdio"
LOG_LEVEL = "DEBUG"  # 开发时用DEBUG
\`\`\`

### 普通用户

使用pipx安装，稳定可靠：

\`\`\`bash
pipx install mingli-mcp
\`\`\`

\`\`\`toml
[mcp_servers.mingli]
command = "mingli-mcp"
startup_timeout_sec = 20
[mcp_servers.mingli.env]
TRANSPORT_TYPE = "stdio"
LOG_LEVEL = "ERROR"  # 生产用ERROR
\`\`\`

---

## ✅ 升级完成检查清单

- [ ] 升级到v1.0.2
- [ ] 验证版本号正确
- [ ] 测试MCP握手成功
- [ ] Codex配置已更新
- [ ] Codex已重启
- [ ] 测试命理功能正常

---

**🎉 恭喜！升级到v1.0.2完成！现在应该可以在Codex中正常使用了！**
