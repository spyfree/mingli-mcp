# Cloudflare Tunnel 配置 - lee.locker 域名

## ⚠️ 重要说明

你提到安装了 **wrangler**，但对于这个Python MCP服务，需要使用的是 **cloudflared**（Cloudflare Tunnel），而不是wrangler（Cloudflare Workers）。

- **Wrangler**: 用于部署JavaScript Workers
- **Cloudflared**: 用于创建安全隧道（支持任何应用）

---

## 🚀 快速开始（使用你的域名 lee.locker）

### 步骤1：安装cloudflared

\`\`\`bash
# macOS
brew install cloudflare/cloudflare/cloudflared

# 验证安装
cloudflared --version
\`\`\`

### 步骤2：登录Cloudflare

\`\`\`bash
cloudflared tunnel login
\`\`\`

会打开浏览器，选择你的域名 **lee.locker**

### 步骤3：创建隧道

\`\`\`bash
# 创建名为 mingli-mcp 的隧道
cloudflared tunnel create mingli-mcp

# 会输出类似：
# Tunnel credentials written to ~/.cloudflared/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.json
# Created tunnel mingli-mcp with id xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
\`\`\`

**记下这个UUID**，下面会用到。

### 步骤4：配置DNS

\`\`\`bash
# 将子域名 mcp.lee.locker 指向你的隧道
cloudflared tunnel route dns mingli-mcp mcp.lee.locker
\`\`\`

### 步骤5：创建配置文件

创建 \`~/.cloudflared/config.yml\`：

\`\`\`yaml
tunnel: mingli-mcp
credentials-file: ~/.cloudflared/你的UUID.json

ingress:
  - hostname: mcp.lee.locker
    service: http://localhost:8080
  - service: http_status:404
\`\`\`

### 步骤6：启动服务

**终端1 - 启动MCP服务**：
\`\`\`bash
cd /Users/lix18854/Documents/code/ziwei_mcp
source venv/bin/activate
export TRANSPORT_TYPE=http
export HTTP_PORT=8080
python mingli_mcp.py
\`\`\`

**终端2 - 启动隧道**：
\`\`\`bash
cloudflared tunnel run mingli-mcp
\`\`\`

### 步骤7：测试访问

\`\`\`bash
# 测试健康检查
curl https://mcp.lee.locker/health

# 应该返回：
# {"status": "healthy", "transport": "http", "systems": ["ziwei", "bazi"]}
\`\`\`

---

## 🎯 在Coze配置

\`\`\`json
{
  "mcpServers": {
    "mingli": {
      "url": "https://mcp.lee.locker/mcp",
      "headers": {
        "Content-Type": "application/json"
      }
    }
  }
}
\`\`\`

---

## 🔧 开机自启动（可选）

### macOS

\`\`\`bash
# 安装为系统服务
sudo cloudflared service install

# 启动服务
sudo launchctl start com.cloudflare.cloudflared
\`\`\`

### Linux (systemd)

创建 \`/etc/systemd/system/cloudflared.service\`：

\`\`\`ini
[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=your-username
ExecStart=/usr/local/bin/cloudflared tunnel run mingli-mcp
Restart=on-failure

[Install]
WantedBy=multi-user.target
\`\`\`

启动：
\`\`\`bash
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
\`\`\`

---

## 🔐 添加访问控制（可选）

如果想限制访问，可以在配置中添加：

\`\`\`yaml
tunnel: mingli-mcp
credentials-file: ~/.cloudflared/你的UUID.json

ingress:
  - hostname: mcp.lee.locker
    service: http://localhost:8080
    originRequest:
      # 可以添加认证
      noTLSVerify: false
  - service: http_status:404
\`\`\`

然后在MCP服务中启用API密钥：

\`\`\`bash
export HTTP_API_KEY=your-secret-key-here
python mingli_mcp.py
\`\`\`

Coze配置中添加认证：

\`\`\`json
{
  "mcpServers": {
    "mingli": {
      "url": "https://mcp.lee.locker/mcp",
      "headers": {
        "Content-Type": "application/json",
        "Authorization": "Bearer your-secret-key-here"
      }
    }
  }
}
\`\`\`

---

## 📊 监控隧道状态

\`\`\`bash
# 查看隧道信息
cloudflared tunnel info mingli-mcp

# 查看运行日志
cloudflared tunnel run mingli-mcp --loglevel debug
\`\`\`

在Cloudflare Dashboard查看：
https://dash.cloudflare.com → Zero Trust → Access → Tunnels

---

## 🐛 常见问题

### Q: DNS记录未生效
**A**: 等待几分钟，DNS记录需要时间传播

\`\`\`bash
# 检查DNS
nslookup mcp.lee.locker
\`\`\`

### Q: 连接失败
**A**: 确保：
1. MCP服务正在运行（8080端口）
2. Cloudflare隧道正在运行
3. 配置文件路径正确

\`\`\`bash
# 检查MCP服务
curl http://localhost:8080/health

# 检查隧道
cloudflared tunnel info mingli-mcp
\`\`\`

### Q: 想临时测试
**A**: 使用快速模式（无需配置）：

\`\`\`bash
# 启动MCP服务
python mingli_mcp.py &

# 临时隧道（会生成随机域名）
cloudflared tunnel --url http://localhost:8080
\`\`\`

---

## 📚 参考资源

- [Cloudflare Tunnel文档](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Zero Trust Dashboard](https://dash.cloudflare.com)

---

**🎉 完成后，你的MCP服务将通过 https://mcp.lee.locker 访问！**
