# Coze (扣子) MCP配置专用指南

## 🎯 Coze平台说明

Coze是字节跳动推出的AI聊天机器人开发平台，支持多种集成方式。

**平台地址**：
- 国内版：https://www.coze.cn/
- 国际版：https://coze.com/

---

## 📋 Coze支持的MCP配置方式

Coze可能支持以下几种方式（具体以平台实际支持为准）：

### 方式1：HTTP端点（推荐）⭐⭐⭐⭐⭐

适用于云端部署，最稳定可靠。

### 方式2：命令行调用

如果Coze支持类似Claude Desktop的stdio模式。

### 方式3：插件集成

通过Coze的插件市场或自定义插件。

---

## 🚀 方式1：使用HTTP端点（Cloudflare Tunnel）

### 步骤1：启动本地服务

**终端1**：
\`\`\`bash
cd /Users/lix18854/Documents/code/ziwei_mcp
source venv/bin/activate
export TRANSPORT_TYPE=http
export HTTP_PORT=8080
python mingli_mcp.py
\`\`\`

**终端2**：
\`\`\`bash
cloudflared tunnel run mingli-mcp
\`\`\`

### 步骤2：验证服务

\`\`\`bash
curl https://your-mcp.example/health
# 应该返回：{"status":"healthy","transport":"http","systems":["ziwei","bazi"]}
\`\`\`

### 步骤3：在Coze配置

#### 如果Coze使用JSON配置

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

#### 如果Coze使用表单配置

填写以下信息：

| 字段 | 值 |
|------|-----|
| 服务名称 | 命理MCP服务 |
| 协议类型 | MCP / HTTP |
| 端点URL | https://your-mcp.example/mcp |
| 请求方法 | POST |
| Content-Type | application/json |

---

## 🚀 方式2：使用PyPI包（如果支持）

### 步骤1：确认Coze支持命令行模式

检查Coze文档是否支持类似Claude Desktop的stdio配置。

### 步骤2：配置JSON

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

### 步骤3：测试

在Coze对话中尝试：
\`\`\`
列出可用的命理系统
\`\`\`

---

## 🚀 方式3：部署到云端（Railway）

如果你不想保持本地服务运行，可以部署到Railway。

### 步骤1：部署到Railway

1. 访问 https://railway.app
2. 连接GitHub：spyfree/mingli-mcp
3. 设置环境变量：
   \`\`\`
   TRANSPORT_TYPE=http
   HTTP_PORT=8080
   \`\`\`
4. 部署完成，获得URL：\`https://yourapp.railway.app\`

### 步骤2：在Coze配置

\`\`\`json
{
  "mcpServers": {
    "mingli": {
      "url": "https://yourapp.railway.app/mcp",
      "method": "POST",
      "headers": {
        "Content-Type": "application/json"
      }
    }
  }
}
\`\`\`

**优势**：
- ✅ 24/7运行
- ✅ 无需本地服务
- ✅ 自动重启
- 💰 $5/月

---

## 📝 Coze配置示例

### 配置格式A（JSON配置文件）

如果Coze支持上传或粘贴JSON配置文件：

\`\`\`json
{
  "version": "1.0",
  "mcpServers": {
    "mingli": {
      "name": "命理MCP服务",
      "description": "提供紫微斗数和八字分析",
      "transport": "http",
      "url": "https://your-mcp.example/mcp",
      "method": "POST",
      "headers": {
        "Content-Type": "application/json"
      },
      "timeout": 30000
    }
  }
}
\`\`\`

### 配置格式B（YAML配置）

如果Coze使用YAML格式：

\`\`\`yaml
mcpServers:
  mingli:
    name: 命理MCP服务
    description: 提供紫微斗数和八字分析
    transport: http
    url: https://your-mcp.example/mcp
    method: POST
    headers:
      Content-Type: application/json
    timeout: 30000
\`\`\`

### 配置格式C（网页表单）

如果Coze通过网页表单配置：

**基本信息**：
- 服务ID：\`mingli\`
- 服务名称：\`命理MCP服务\`
- 描述：\`提供紫微斗数、八字等命理分析服务\`

**连接配置**：
- 协议：\`MCP over HTTP\`
- 端点地址：\`https://your-mcp.example/mcp\`
- 请求方法：\`POST\`
- 超时时间：\`30秒\`

**请求头**：
- \`Content-Type: application/json\`

---

## 🧪 测试MCP服务

### 测试1：健康检查

直接访问健康检查端点：
\`\`\`bash
curl https://your-mcp.example/health
\`\`\`

**预期响应**：
\`\`\`json
{
  "status": "healthy",
  "transport": "http",
  "systems": ["ziwei", "bazi"]
}
\`\`\`

### 测试2：MCP初始化

\`\`\`bash
curl -X POST https://your-mcp.example/mcp \\
  -H "Content-Type: application/json" \\
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "clientInfo": {
        "name": "coze-test",
        "version": "1.0.0"
      }
    }
  }'
\`\`\`

### 测试3：列出工具

\`\`\`bash
curl -X POST https://your-mcp.example/mcp \\
  -H "Content-Type: application/json" \\
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'
\`\`\`

### 测试4：调用功能

\`\`\`bash
curl -X POST https://your-mcp.example/mcp \\
  -H "Content-Type: application/json" \\
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "list_fortune_systems",
      "arguments": {}
    }
  }'
\`\`\`

---

## 🎯 在Coze中使用

配置完成后，在Coze对话中可以这样使用：

### 示例对话1：列出系统

**用户**：\`列出所有可用的命理系统\`

**预期**：Coze调用\`list_fortune_systems\`工具，返回紫微斗数和八字系统。

### 示例对话2：紫微排盘

**用户**：\`帮我排一个紫微斗数盘，我是2000年8月16日寅时出生的女生\`

**预期**：Coze调用\`get_ziwei_chart\`工具，返回完整命盘。

### 示例对话3：八字分析

**用户**：\`分析一下我的八字五行，2000-08-16寅时，女\`

**预期**：Coze调用\`analyze_bazi_element\`工具，返回五行分析。

---

## 🐛 Coze常见问题

### 问题1：无法连接到MCP服务

**检查清单**：
1. ✅ 本地MCP服务是否运行？
   \`\`\`bash
   curl http://localhost:8080/health
   \`\`\`

2. ✅ Cloudflare隧道是否运行？
   \`\`\`bash
   ps aux | grep cloudflared
   \`\`\`

3. ✅ 域名是否正常解析？
   \`\`\`bash
   curl https://your-mcp.example/health
   \`\`\`

### 问题2：Coze提示工具不可用

**可能原因**：
- MCP服务未正确初始化
- 配置格式错误
- 网络连接问题

**解决方案**：
1. 检查配置JSON格式
2. 测试MCP端点是否可访问
3. 查看Coze控制台日志

### 问题3：调用超时

**原因**：网络延迟或计算时间长

**解决**：
- 增加超时时间配置
- 优化代码性能
- 考虑部署到离用户更近的区域

---

## 📊 配置方案对比

| 方案 | 优势 | 劣势 | 成本 | 推荐度 |
|------|------|------|------|--------|
| **Cloudflare Tunnel** | 免费、快速 | 需本地运行 | 免费 | ⭐⭐⭐⭐⭐ |
| **Railway部署** | 24/7运行 | 需付费 | $5/月 | ⭐⭐⭐⭐ |
| **PyPI包（stdio）** | 标准方式 | 依赖Coze支持 | 免费 | ⭐⭐⭐ |

---

## 💡 推荐配置

### 个人测试

使用Cloudflare Tunnel：
\`\`\`json
{
  "mcpServers": {
    "mingli": {
      "url": "https://your-mcp.example/mcp"
    }
  }
}
\`\`\`

### 商业使用

部署到Railway并配置：
\`\`\`json
{
  "mcpServers": {
    "mingli": {
      "url": "https://yourapp.railway.app/mcp"
    }
  }
}
\`\`\`

---

## 📞 需要帮助？

1. **查看Coze官方文档**
   - 国内版：https://www.coze.cn/docs
   - 国际版：https://docs.coze.com/

2. **查看项目文档**
   - GitHub：https://github.com/spyfree/mingli-mcp
   - README：完整使用说明

3. **创建Issue**
   - 遇到问题在GitHub创建Issue
   - 详细描述问题和配置

---

**祝你在Coze上使用愉快！** 🎉
