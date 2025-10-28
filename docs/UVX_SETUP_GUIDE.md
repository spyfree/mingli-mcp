# Mingli MCP Server UVX 配置指南

## 📦 快速配置 mingli-mcp (uvx 方式)

### 1. 安装 uvx (如果没有安装)

**使用 pipx (推荐):**
```bash
pip install pipx
pipx install uv
```

**或者使用 pip:**
```bash
pip install uv
```

**或者使用 Homebrew (macOS):**
```bash
brew install uv
```

### 2. 配置 MCP 客户端

#### 对于 Cursor IDE:

创建或编辑配置文件 `~/.cursor/mcp.json`:

```bash
# 创建目录（如果不存在）
mkdir -p ~/.cursor

# 创建配置文件
cat > ~/.cursor/mcp.json << 'EOF'
{
  "mcpServers": {
    "mingli": {
      "command": "uvx",
      "args": ["mingli-mcp"],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
EOF
```

#### 对于 Claude Code:

```bash
claude mcp add mingli -- uvx mingli-mcp
```

#### 对于 OpenAI Codex:

```bash
codex mcp add mingli -- uvx mingli-mcp
```

### 3. 重启你的 IDE

重启 Cursor IDE 以加载新的 MCP 配置。

### 4. 验证配置

在 Cursor 中新建对话，输入：

```
帮我排一个紫微斗数盘：2000年8月16日，寅时，女性
```

如果能正常返回排盘结果，说明配置成功！

## 🔧 可用功能

### 紫微斗数功能
- **get_ziwei_chart**: 获取完整紫微斗数排盘
- **get_ziwei_fortune**: 查询运势（大限、流年、流月等）
- **analyze_ziwei_palace**: 分析特定宫位

### 八字功能 ⭐ **新增**
- **get_bazi_chart**: 获取四柱八字排盘
- **get_bazi_fortune**: 查询八字运势
- **analyze_bazi_element**: 分析五行强弱

### 通用功能
- **list_fortune_systems**: 列出所有可用命理系统

## 📝 使用示例

### 紫微斗数查询

**排盘:**
```
帮我排一个紫微斗数盘：1990年5月20日，午时，男性
```

**查询运势:**
```
查询这个人今年的运势如何
```

**分析宫位:**
```
分析他的财帛宫
```

### 八字查询

**排盘:**
```
帮我算八字：1985年3月15日，卯时，女性
```

**五行分析:**
```
分析一下她的五行缺什么
```

**运势查询:**
```
看看她今年的大运
```

### 农历支持

**农历排盘:**
```
排盘：农历1995年7月初七，酉时，女性
```

## 🛠️ 故障排除

### 1. 检查 uvx 是否可用
```bash
which uvx
# 如果没有输出，需要安装 uv
```

### 2. 测试 mingli-mcp
```bash
uvx mingli-mcp --help
```

### 3. 查看日志
mingli-mcp 支持多种日志级别：
- `DEBUG`: 最详细的日志
- `INFO`: 一般信息（推荐）
- `WARNING`: 只显示警告
- `ERROR`: 只显示错误

在配置文件中修改 `LOG_LEVEL`:
```json
{
  "mcpServers": {
    "mingli": {
      "command": "uvx",
      "args": ["mingli-mcp"],
      "env": {
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### 4. 常见问题

**Q: 提示 "uvx not found"**
A: 需要安装 uv。运行 `pip install uv` 或使用上面提到的安装方法。

**Q: mingli-mcp 无法启动**
A: 检查日志信息，通常是依赖问题。尝试重新安装：
```bash
uvx --no-cache mingli-mcp
```

**Q: 在 Cursor 中看不到工具**
A: 确保配置了正确的路径 ~/.cursor/mcp.json，然后重启 Cursor。

## 📚 更多信息

- 项目主页: https://github.com/spyfree/mingli-mcp
- 在线演示: https://server.smithery.ai/@spyfree/mingli-mcp/mcp
- 问题反馈: https://github.com/spyfree/mingli-mcp/issues

## 🎯 快速安装按钮

**一键添加到 Cursor:**
[![Install MCP Server](https://img.shields.io/badge/Cursor-Add+MCP+Server-blue?logo=cursor)](https://cursor.com/install-mcp?name=mingli&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyJtaW5nbGktbWNwIl19)

## 版本历史

- **v1.0.5**: 修复依赖问题，包含 uvicorn 和 fastapi
- **v1.0.4**: 添加 HTTP 传输支持
- **v1.0.3**: 完善八字系统
- **v1.0.2**: 性能优化
- **v1.0.1**: 修复 bug
- **v1.0.0**: 初始版本

---

**🔮 享受你的命理探索之旅！**
