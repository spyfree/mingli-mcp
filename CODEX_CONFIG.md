# Codex MCP 配置指南

## 🎯 Codex配置格式

Codex使用 **TOML** 格式配置文件，而不是JSON。

**配置文件位置**：
```
~/.codex/config.toml
```

---

## ⚠️ 超时问题解决

### 问题原因

错误信息：
```
MCP client for `mingli` timed out after 10 seconds.
```

**原因分析**：
1. **首次启动慢**：uvx需要下载和安装包（可能需要20-30秒）
2. **依赖多**：mingli-mcp有多个Python依赖（py-iztro, lunar_python等）
3. **默认超时短**：Codex默认10秒超时

---

## ✅ 解决方案

### 方案1：增加超时时间（最简单）⭐⭐⭐⭐⭐

编辑 \`~/.codex/config.toml\`：

\`\`\`toml
[mcp_servers.mingli]
command = "uvx"
args = ["mingli-mcp@1.0.1"]
startup_timeout_sec = 60  # 增加到60秒

[mcp_servers.mingli.env]
TRANSPORT_TYPE = "stdio"
LOG_LEVEL = "INFO"
\`\`\`

**首次启动可能更长，建议设置更大**：

\`\`\`toml
[mcp_servers.mingli]
command = "uvx"
args = ["mingli-mcp@1.0.1"]
startup_timeout_sec = 120  # 首次启动设置120秒
\`\`\`

---

### 方案2：预安装包（推荐）⭐⭐⭐⭐⭐

先用pipx全局安装，启动就会很快。

#### 步骤1：安装pipx和包

\`\`\`bash
# 安装pipx（如果没有）
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# 安装mingli-mcp
pipx install mingli-mcp

# 验证安装
mingli-mcp --help
\`\`\`

#### 步骤2：配置Codex

\`\`\`toml
[mcp_servers.mingli]
command = "mingli-mcp"  # 直接调用命令
startup_timeout_sec = 15  # 预安装后启动很快

[mcp_servers.mingli.env]
TRANSPORT_TYPE = "stdio"
LOG_LEVEL = "INFO"
\`\`\`

或使用完整路径：

\`\`\`toml
[mcp_servers.mingli]
command = "/Users/lix18854/.local/bin/mingli-mcp"  # pipx安装路径
startup_timeout_sec = 15
\`\`\`

找到安装路径：
\`\`\`bash
which mingli-mcp
# 输出：/Users/lix18854/.local/bin/mingli-mcp
\`\`\`

---

### 方案3：使用本地开发版本（最快）⭐⭐⭐⭐⭐

直接使用你本地的代码：

\`\`\`toml
[mcp_servers.mingli]
command = "/Users/lix18854/Documents/code/ziwei_mcp/venv/bin/python"
args = ["/Users/lix18854/Documents/code/ziwei_mcp/mingli_mcp.py"]
startup_timeout_sec = 15  # 本地启动很快

[mcp_servers.mingli.env]
TRANSPORT_TYPE = "stdio"
LOG_LEVEL = "INFO"
\`\`\`

**优势**：
- ✅ 启动最快（2-3秒）
- ✅ 代码修改立即生效
- ✅ 便于调试

---

### 方案4：使用uv cache（加速uvx）

预先缓存uvx环境：

\`\`\`bash
# 先手动运行一次，让uvx下载和缓存包
uvx mingli-mcp@1.0.1 --help

# 然后配置Codex
\`\`\`

\`\`\`toml
[mcp_servers.mingli]
command = "uvx"
args = ["mingli-mcp@1.0.1"]
startup_timeout_sec = 30  # 第二次启动会快很多
\`\`\`

---

## 📝 完整配置示例

### 推荐配置（方案2：pipx预安装）

\`\`\`toml
# ~/.codex/config.toml

[mcp_servers.mingli]
command = "mingli-mcp"
startup_timeout_sec = 20

[mcp_servers.mingli.env]
TRANSPORT_TYPE = "stdio"
LOG_LEVEL = "INFO"
\`\`\`

### 开发配置（方案3：本地路径）

\`\`\`toml
# ~/.codex/config.toml

[mcp_servers.mingli]
command = "/Users/lix18854/Documents/code/ziwei_mcp/venv/bin/python"
args = ["/Users/lix18854/Documents/code/ziwei_mcp/mingli_mcp.py"]
startup_timeout_sec = 15

[mcp_servers.mingli.env]
TRANSPORT_TYPE = "stdio"
LOG_LEVEL = "DEBUG"
\`\`\`

### uvx配置（方案1：增加超时）

\`\`\`toml
# ~/.codex/config.toml

[mcp_servers.mingli]
command = "uvx"
args = ["mingli-mcp@1.0.1"]
startup_timeout_sec = 120  # 首次启动用120秒

[mcp_servers.mingli.env]
TRANSPORT_TYPE = "stdio"
\`\`\`

---

## 🔧 优化启动脚本

创建一个快速启动脚本：

\`\`\`bash
# ~/.local/bin/mingli-mcp-fast.sh
#!/bin/bash
cd /Users/lix18854/Documents/code/ziwei_mcp
source venv/bin/activate
exec python mingli_mcp.py "$@"
\`\`\`

\`\`\`bash
chmod +x ~/.local/bin/mingli-mcp-fast.sh
\`\`\`

配置Codex：

\`\`\`toml
[mcp_servers.mingli]
command = "/Users/lix18854/.local/bin/mingli-mcp-fast.sh"
startup_timeout_sec = 10
\`\`\`

---

## 🧪 测试配置

### 步骤1：编辑配置

\`\`\`bash
nano ~/.codex/config.toml
\`\`\`

### 步骤2：重启Codex

完全退出并重新打开Codex。

### 步骤3：查看日志

如果还有问题，查看Codex日志：

\`\`\`bash
# Codex日志位置（具体路径可能不同）
tail -f ~/.codex/logs/mcp.log
\`\`\`

### 步骤4：测试调用

在Codex中尝试：

\`\`\`
列出所有可用的命理系统
\`\`\`

---

## 🐛 常见问题

### 问题1：找不到config.toml

**解决**：创建目录和文件

\`\`\`bash
mkdir -p ~/.codex
touch ~/.codex/config.toml
nano ~/.codex/config.toml
\`\`\`

### 问题2：还是超时

**调试步骤**：

\`\`\`bash
# 1. 手动测试命令
time uvx mingli-mcp@1.0.1 --help
# 看看实际需要多少秒

# 2. 如果第一次很慢，第二次测试
time uvx mingli-mcp@1.0.1 --help
# 应该会快很多

# 3. 设置超时为实际时间的2倍
# 例如实际需要30秒，设置60秒
\`\`\`

### 问题3：命令找不到

**检查路径**：

\`\`\`bash
# 检查uvx
which uvx

# 检查mingli-mcp（如果用pipx安装）
which mingli-mcp

# 检查Python
which python3
\`\`\`

如果找不到，使用完整路径：

\`\`\`toml
[mcp_servers.mingli]
command = "/Users/lix18854/.local/bin/uvx"  # 完整路径
args = ["mingli-mcp@1.0.1"]
startup_timeout_sec = 60
\`\`\`

---

## 📊 启动时间对比

| 方式 | 首次启动 | 后续启动 | 推荐超时 |
|------|---------|---------|---------|
| **uvx（无缓存）** | 30-60秒 | 20-30秒 | 120秒 |
| **uvx（有缓存）** | 20-30秒 | 10-15秒 | 60秒 |
| **pipx预安装** | 5-10秒 | 3-5秒 | 20秒 |
| **本地路径** | 2-3秒 | 2-3秒 | 15秒 |

---

## 💡 最佳实践推荐

### 生产使用（稳定优先）

\`\`\`bash
# 1. 预安装
pipx install mingli-mcp

# 2. 配置
[mcp_servers.mingli]
command = "mingli-mcp"
startup_timeout_sec = 20
\`\`\`

### 开发调试（速度优先）

\`\`\`toml
[mcp_servers.mingli]
command = "/Users/lix18854/Documents/code/ziwei_mcp/venv/bin/python"
args = ["/Users/lix18854/Documents/code/ziwei_mcp/mingli_mcp.py"]
startup_timeout_sec = 15

[mcp_servers.mingli.env]
LOG_LEVEL = "DEBUG"
\`\`\`

---

## ✅ 立即行动

### 快速修复（30秒）

\`\`\`bash
# 编辑配置
nano ~/.codex/config.toml

# 添加这几行
[mcp_servers.mingli]
command = "uvx"
args = ["mingli-mcp@1.0.1"]
startup_timeout_sec = 120  # 关键：增加超时！

# 保存并重启Codex
\`\`\`

### 永久优化（5分钟）

\`\`\`bash
# 1. 安装pipx
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# 2. 安装包
pipx install mingli-mcp

# 3. 配置Codex
nano ~/.codex/config.toml

[mcp_servers.mingli]
command = "mingli-mcp"
startup_timeout_sec = 20

# 4. 重启Codex
\`\`\`

---

## 📞 还有问题？

### 查看详细错误

在配置中启用详细日志：

\`\`\`toml
[mcp_servers.mingli]
command = "uvx"
args = ["mingli-mcp@1.0.1"]
startup_timeout_sec = 120

[mcp_servers.mingli.env]
LOG_LEVEL = "DEBUG"
\`\`\`

### 手动测试MCP协议

\`\`\`bash
# 测试stdio模式
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | mingli-mcp
\`\`\`

---

**建议：先用方案1（增加超时到120秒）快速修复，后续再用方案2（pipx预安装）永久优化！** 🚀
