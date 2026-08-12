# MCP客户端配置指南

## 📋 支持的MCP客户端

本文档包含以下客户端的配置：

1. **Claude Desktop** - Anthropic官方桌面应用
2. **Coze (扣子)** - 字节跳动AI平台  
3. **Cursor** - AI代码编辑器
4. **通用MCP客户端**

---

## 1. Claude Desktop 配置

### 配置文件位置

**macOS**:
\`\`\`
~/Library/Application Support/Claude/claude_desktop_config.json
\`\`\`

**Windows**:
\`\`\`
%APPDATA%/Claude/claude_desktop_config.json
\`\`\`

### 使用PyPI包（推荐）

\`\`\`json
{
  "mcpServers": {
    "mingli": {
      "command": "uvx",
      "args": ["mingli-mcp@1.0.1"]
    }
  }
}
\`\`\`

或使用pipx：

\`\`\`json
{
  "mcpServers": {
    "mingli": {
      "command": "pipx",
      "args": ["run", "mingli-mcp==1.0.1"]
    }
  }
}
\`\`\`

或使用本地Python环境：

\`\`\`json
{
  "mcpServers": {
    "mingli": {
      "command": "python",
      "args": ["-m", "mingli_mcp"],
      "env": {
        "TRANSPORT_TYPE": "stdio",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
\`\`\`

### 使用本地开发版本

\`\`\`json
{
  "mcpServers": {
    "mingli": {
      "command": "/Users/lix18854/Documents/code/ziwei_mcp/venv/bin/python",
      "args": ["/Users/lix18854/Documents/code/ziwei_mcp/mingli_mcp.py"],
      "env": {
        "TRANSPORT_TYPE": "stdio"
      }
    }
  }
}
\`\`\`

### 完整配置示例（多个服务器）

\`\`\`json
{
  "mcpServers": {
    "mingli": {
      "command": "uvx",
      "args": ["mingli-mcp@1.0.1"],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/files"]
    }
  }
}
\`\`\`

---

## 2. Coze (扣子) 配置

Coze支持两种方式配置MCP服务器：

### 方式A：使用PyPI包（stdio模式）

如果Coze支持命令行方式（类似Claude Desktop）：

\`\`\`json
{
  "mcpServers": {
    "mingli": {
      "command": "uvx",
      "args": ["mingli-mcp@1.0.1"]
    }
  }
}
\`\`\`

### 方式B：使用HTTP端点（推荐）

如果Coze主要支持HTTP方式：

\`\`\`json
{
  "mcpServers": {
    "mingli": {
      "url": "https://your-mcp.example/mcp",
      "method": "POST",
      "headers": {
        "Content-Type": "application/json"
      }
    }
  }
}
\`\`\`

### Coze网页版配置

在Coze网页版的插件配置中：

\`\`\`yaml
服务名称: 命理MCP服务
协议类型: MCP
连接方式: HTTP
端点地址: https://your-mcp.example/mcp
请求方法: POST
请求头:
  Content-Type: application/json
\`\`\`

---

## 3. Cursor 配置

### 配置文件位置

**macOS/Linux**:
\`\`\`
~/.cursor/mcp_config.json
\`\`\`

**Windows**:
\`\`\`
%USERPROFILE%/.cursor/mcp_config.json
\`\`\`

### 配置内容

\`\`\`json
{
  "mcpServers": {
    "mingli": {
      "command": "uvx",
      "args": ["mingli-mcp@1.0.1"],
      "env": {
        "TRANSPORT_TYPE": "stdio"
      }
    }
  }
}
\`\`\`

或在项目根目录创建 \`.cursor/mcp_config.json\`：

\`\`\`json
{
  "mcpServers": {
    "mingli": {
      "command": "python",
      "args": ["-m", "mingli_mcp"]
    }
  }
}
\`\`\`

---

## 4. 通用MCP客户端配置

### stdio传输模式（命令行）

适用于：Claude Desktop、Cursor等桌面应用

\`\`\`json
{
  "mcpServers": {
    "mingli": {
      "command": "mingli-mcp",
      "args": [],
      "env": {
        "TRANSPORT_TYPE": "stdio",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
\`\`\`

### HTTP传输模式（网络请求）

适用于：Coze、网页客户端、远程调用

\`\`\`json
{
  "mcpServers": {
    "mingli": {
      "url": "https://your-mcp.example/mcp",
      "transport": "http",
      "headers": {
        "Content-Type": "application/json"
      }
    }
  }
}
\`\`\`

---

## 🔧 安装前置要求

### 使用uvx（推荐）

\`\`\`bash
# 安装uv（如果没有）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 测试uvx
uvx --version
\`\`\`

### 使用pipx

\`\`\`bash
# 安装pipx（如果没有）
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# 安装mingli-mcp
pipx install mingli-mcp

# 测试
mingli-mcp --help
\`\`\`

### 使用pip

\`\`\`bash
# 全局安装
pip install mingli-mcp

# 或在虚拟环境中
python3 -m venv venv
source venv/bin/activate
pip install mingli-mcp
\`\`\`

---

## 📝 配置步骤

### Claude Desktop

1. **找到配置文件**
   \`\`\`bash
   # macOS
   open ~/Library/Application\ Support/Claude/
   
   # 如果文件不存在，创建它
   touch ~/Library/Application\ Support/Claude/claude_desktop_config.json
   \`\`\`

2. **编辑配置**
   \`\`\`bash
   nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
   \`\`\`
   
   粘贴配置内容（见上方示例）

3. **重启Claude Desktop**

4. **验证**
   - 打开Claude Desktop
   - 查看是否有MCP工具图标
   - 尝试使用命理功能

### Coze

1. **登录Coze平台**
   https://www.coze.cn/ 或 https://coze.com/

2. **进入Bot配置**
   - 创建或编辑Bot
   - 找到"插件"或"MCP服务器"配置

3. **添加MCP服务器**
   - 名称：命理MCP服务
   - 类型：选择HTTP或命令行（根据平台支持）
   - 配置：粘贴对应的JSON配置

4. **测试连接**
   - 保存配置
   - 测试调用命理功能

### Cursor

1. **创建配置文件**
   \`\`\`bash
   mkdir -p ~/.cursor
   nano ~/.cursor/mcp_config.json
   \`\`\`

2. **粘贴配置**
   （见上方Cursor配置示例）

3. **重启Cursor**

4. **测试**
   - 打开命令面板（Cmd/Ctrl+Shift+P）
   - 查找MCP相关命令
   - 或在AI聊天中直接使用

---

## 🧪 测试配置

### 测试命令

配置完成后，在客户端中尝试这些命令：

\`\`\`
1. 列出所有可用的命理系统
2. 帮我排一个紫微斗数盘：2000年8月16日，寅时，女性
3. 帮我看看八字：2000-08-16，寅时，女
4. 分析这个八字的五行：2000年8月16日寅时女性
\`\`\`

### 预期结果

客户端应该能够：
- ✅ 识别MCP服务器
- ✅ 列出可用工具
- ✅ 调用命理分析功能
- ✅ 返回格式化的结果

---

## 🐛 常见问题

### 问题1：找不到命令 mingli-mcp

**原因**：包未安装或不在PATH中

**解决**：
\`\`\`bash
# 检查安装
pip show mingli-mcp

# 如果没有，安装
pip install mingli-mcp

# 或使用完整路径
which mingli-mcp

# 在配置中使用完整路径
"command": "/path/to/mingli-mcp"
\`\`\`

### 问题2：uvx命令不可用

**原因**：uv未安装

**解决**：
\`\`\`bash
# 安装uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或改用pipx
"command": "pipx",
"args": ["run", "mingli-mcp"]
\`\`\`

### 问题3：客户端无法连接

**原因**：配置格式错误或路径不对

**解决**：
\`\`\`bash
# 验证JSON格式
python3 -c "import json; json.load(open('config.json'))"

# 测试命令是否可执行
mingli-mcp --help

# 查看日志
export LOG_LEVEL=DEBUG
mingli-mcp
\`\`\`

### 问题4：权限错误

**原因**：Python环境或文件权限问题

**解决**：
\`\`\`bash
# 检查权限
ls -la $(which mingli-mcp)

# 修复权限
chmod +x $(which mingli-mcp)

# 或使用python -m方式
"command": "python",
"args": ["-m", "mingli_mcp"]
\`\`\`

---

## 📊 配置对比

| 客户端 | 推荐方式 | 配置位置 | 传输模式 |
|--------|---------|---------|---------|
| **Claude Desktop** | uvx/pipx | \`~/Library/Application Support/Claude/\` | stdio |
| **Coze** | HTTP端点 | 平台网页配置 | HTTP |
| **Cursor** | uvx/python | \`~/.cursor/mcp_config.json\` | stdio |
| **通用客户端** | 根据支持 | 客户端特定位置 | stdio或HTTP |

---

## 💡 推荐配置

### 开发测试

\`\`\`json
{
  "mcpServers": {
    "mingli": {
      "command": "/Users/lix18854/Documents/code/ziwei_mcp/venv/bin/python",
      "args": ["/Users/lix18854/Documents/code/ziwei_mcp/mingli_mcp.py"],
      "env": {
        "TRANSPORT_TYPE": "stdio",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
\`\`\`

### 生产使用

\`\`\`json
{
  "mcpServers": {
    "mingli": {
      "command": "uvx",
      "args": ["mingli-mcp@1.0.1"],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
\`\`\`

### Coze云端

\`\`\`json
{
  "mcpServers": {
    "mingli": {
      "url": "https://your-mcp.example/mcp"
    }
  }
}
\`\`\`

---

## 📚 更多资源

- MCP协议文档：https://modelcontextprotocol.io/
- Claude Desktop：https://claude.ai/download
- Coze平台：https://www.coze.cn/
- 项目GitHub：https://github.com/spyfree/mingli-mcp

---

需要帮助？查看项目README或创建Issue！
