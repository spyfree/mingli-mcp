# Cloudflare 部署指南

## 🌟 推荐方案：Cloudflare Tunnel（零信任访问）

Cloudflare Tunnel 可以把本地服务安全地暴露到公网，**完全免费**且功能强大。

### ✨ 优势

- ✅ **完全免费** - 无限流量
- ✅ **无需公网IP** - 通过隧道连接
- ✅ **自动HTTPS** - 免费SSL证书
- ✅ **DDoS防护** - Cloudflare全球网络
- ✅ **访问控制** - 可配置认证
- ✅ **本地运行** - 代码在你的机器上

### 📋 前置条件

1. 注册Cloudflare账号（免费）：https://dash.cloudflare.com/sign-up
2. （可选）有自己的域名，并添加到Cloudflare

---

## 🚀 快速部署步骤

### 步骤1：安装 cloudflared

#### macOS
```bash
brew install cloudflare/cloudflare/cloudflared
```

#### Linux
```bash
# Debian/Ubuntu
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# CentOS/RHEL
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-x86_64.rpm
sudo rpm -i cloudflared-linux-x86_64.rpm
```

#### Windows
```powershell
# 下载安装器
https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe
```

### 步骤2：登录 Cloudflare

```bash
cloudflared tunnel login
```

会打开浏览器让你选择域名（如果没有域名，可以使用Cloudflare提供的免费域名）。

### 步骤3：创建隧道

```bash
# 创建一个名为 mingli-mcp 的隧道
cloudflared tunnel create mingli-mcp

# 会生成一个 UUID，记下来（类似：xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx）
```

### 步骤4：配置隧道

创建配置文件 `~/.cloudflared/config.yml`：

```yaml
tunnel: mingli-mcp
credentials-file: ~/.cloudflared/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.json

ingress:
  # 如果有自己的域名
  - hostname: mcp.yourdomain.com
    service: http://localhost:8080
  # 如果没有域名，使用trycloudflare（临时）
  - service: http://localhost:8080
```

### 步骤5：配置DNS（如果有域名）

```bash
# 添加DNS记录
cloudflared tunnel route dns mingli-mcp mcp.yourdomain.com
```

### 步骤6：启动服务

```bash
# 终端1：启动你的MCP服务
cd /Users/lix18854/Documents/code/ziwei_mcp
source venv/bin/activate
export TRANSPORT_TYPE=http
export HTTP_PORT=8080
python mingli_mcp.py

# 终端2：启动Cloudflare隧道
cloudflared tunnel run mingli-mcp
```

### 步骤7：测试访问

```bash
# 如果有域名
curl https://mcp.yourdomain.com/health

# 如果使用临时域名，会在启动时显示类似：
# https://random-name.trycloudflare.com
curl https://random-name.trycloudflare.com/health
```

### 步骤8：在Coze配置

```json
{
  "mcpServers": {
    "mingli": {
      "url": "https://mcp.yourdomain.com/mcp",
      "headers": {
        "Content-Type": "application/json"
      }
    }
  }
}
```

---

## 🔧 高级配置

### 使用免费临时域名（快速测试）

如果没有域名，可以使用临时隧道：

```bash
# 启动MCP服务
python mingli_mcp.py

# 另开终端，启动临时隧道
cloudflared tunnel --url http://localhost:8080
```

会生成一个临时URL，有效期24小时。

### 开机自动启动

#### macOS/Linux (systemd)

创建服务文件 `/etc/systemd/system/cloudflared.service`：

```ini
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
```

启动服务：

```bash
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

#### macOS (launchd)

```bash
# cloudflared会自动安装服务
cloudflared service install
```

### 添加访问认证

在 `config.yml` 中添加：

```yaml
tunnel: mingli-mcp
credentials-file: ~/.cloudflared/xxxxxxxx.json

ingress:
  - hostname: mcp.yourdomain.com
    service: http://localhost:8080
    # 添加访问策略
    originRequest:
      noTLSVerify: false
```

然后在Cloudflare Dashboard配置Zero Trust访问策略。

---

## 🎯 方案2：Cloudflare Workers（不推荐）

Cloudflare Workers 主要支持JavaScript，Python支持还在Beta且有限制：

**限制**：
- ❌ CPU时间限制（10-50ms）
- ❌ 内存限制（128MB）
- ❌ 不支持大部分Python库
- ❌ 冷启动时间长

**不适合本项目**，因为：
- py-iztro、lunar_python等库无法运行
- 排盘计算可能超时
- 依赖安装复杂

---

## 💰 成本对比

| 方案 | 费用 | 流量限制 | 稳定性 |
|------|------|---------|--------|
| **Cloudflare Tunnel** | 免费 | 无限 | ⭐⭐⭐⭐⭐ |
| Cloudflare Workers | 免费/付费 | 100k req/day免费 | ⭐⭐⭐ |
| Railway | $5/月 | 有限 | ⭐⭐⭐⭐⭐ |
| Render | 免费/付费 | 休眠 | ⭐⭐⭐⭐ |

---

## 🛡️ 安全建议

### 1. 启用API密钥

```bash
export HTTP_API_KEY=your-secret-key
python mingli_mcp.py
```

### 2. 配置防火墙

```bash
# 只允许Cloudflare IP访问（如果部署在VPS）
# Cloudflare IP列表：https://www.cloudflare.com/ips/
```

### 3. 限制请求频率

在HTTP transport中已实现基础认证，可以添加：

```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/mcp")
@limiter.limit("30/minute")  # 每分钟30次
async def handle_mcp(request: Request):
    ...
```

### 4. 配置Zero Trust

在Cloudflare Dashboard配置访问策略：
- IP白名单
- 邮箱验证
- 一次性PIN
- OAuth集成

---

## 🐛 常见问题

### Q1: 隧道连接失败

**检查**：
```bash
# 查看隧道状态
cloudflared tunnel info mingli-mcp

# 查看日志
cloudflared tunnel run mingli-mcp --loglevel debug
```

### Q2: 本地服务未启动

**确认**：
```bash
# 检查服务是否运行
curl http://localhost:8080/health

# 检查端口占用
lsof -i :8080
```

### Q3: DNS未生效

**等待时间**：DNS记录生效需要几分钟

**验证DNS**：
```bash
nslookup mcp.yourdomain.com
```

---

## 📊 监控和日志

### Cloudflare Dashboard

访问：https://dash.cloudflare.com → Zero Trust → Access → Tunnels

可以看到：
- 连接状态
- 流量统计
- 请求日志
- 错误信息

### 本地日志

```bash
# 查看cloudflared日志
cloudflared tunnel run mingli-mcp --loglevel debug

# 查看MCP服务日志
export LOG_LEVEL=DEBUG
python mingli_mcp.py
```

---

## 🚀 生产部署清单

- [ ] 安装cloudflared
- [ ] 创建隧道
- [ ] 配置DNS（如有域名）
- [ ] 启动MCP服务
- [ ] 启动隧道
- [ ] 测试健康检查
- [ ] 配置开机自启
- [ ] 启用API认证
- [ ] 配置访问策略
- [ ] 在Coze测试
- [ ] 监控日志

---

## 📚 参考资源

- [Cloudflare Tunnel文档](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Zero Trust Dashboard](https://dash.cloudflare.com)
- [Cloudflare Status](https://www.cloudflarestatus.com/)

---

**推荐理由总结**：

Cloudflare Tunnel是**最佳选择**，因为：
1. ✅ 完全免费且稳定
2. ✅ 设置简单（5分钟上手）
3. ✅ 代码在本地运行（完全可控）
4. ✅ 自动HTTPS和DDoS防护
5. ✅ 无需公网IP或云服务器

对于你的项目来说，这是**性价比最高**的方案！
