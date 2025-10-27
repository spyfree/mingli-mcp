# 🔍 部署检查报告

## 检查时间
生成时间：$(date)

## ✅ 检查清单

### 1. PyPI发布检查

**检查命令**：
\`\`\`bash
# 检查包是否存在
curl -s https://pypi.org/pypi/mingli-mcp/json | jq -r '.info.version'

# 测试安装
pip install mingli-mcp --dry-run
\`\`\`

**验证点**：
- [ ] 包在PyPI可见
- [ ] 版本号正确 (1.0.0)
- [ ] 作者信息正确
- [ ] 依赖列表完整

### 2. Cloudflare Tunnel检查

**检查命令**：
\`\`\`bash
# DNS解析
nslookup mcp.lee.locker

# 健康检查
curl https://mcp.lee.locker/health

# 根路径
curl https://mcp.lee.locker/

# MCP端点
curl -X POST https://mcp.lee.locker/mcp \\
  -H "Content-Type: application/json" \\
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
\`\`\`

**验证点**：
- [ ] DNS正确解析
- [ ] HTTPS证书有效
- [ ] 健康检查返回正常
- [ ] MCP端点响应正确

### 3. 功能测试

#### PyPI安装测试

\`\`\`bash
# 创建测试环境
python3 -m venv test_pypi
source test_pypi/bin/activate

# 安装
pip install mingli-mcp

# 测试命令
mingli-mcp --help

# 清理
deactivate
rm -rf test_pypi
\`\`\`

#### Cloudflare端点测试

\`\`\`bash
# 测试紫微斗数
curl -X POST https://mcp.lee.locker/mcp \\
  -H "Content-Type: application/json" \\
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "list_fortune_systems",
      "arguments": {}
    }
  }'
\`\`\`

### 4. Coze集成配置

#### 方式1：使用PyPI包

\`\`\`json
{
  "mcpServers": {
    "mingli": {
      "command": "uvx",
      "args": ["mingli-mcp@1.0.0"],
      "env": {
        "TRANSPORT_TYPE": "stdio",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
\`\`\`

#### 方式2：使用Cloudflare Tunnel

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

### 5. 性能检查

\`\`\`bash
# 响应时间
curl -o /dev/null -s -w "Time: %{time_total}s\\n" https://mcp.lee.locker/health

# 并发测试
for i in {1..10}; do
  curl -s -o /dev/null -w "Request $i: %{time_total}s\\n" https://mcp.lee.locker/health &
done
wait
\`\`\`

---

## 🎯 在Coze中测试

配置好后，在Coze中测试这些命令：

### 测试紫微斗数
\`\`\`
帮我排一个紫微斗数盘：2000年8月16日，寅时，女性
\`\`\`

### 测试八字
\`\`\`
帮我看看八字：2000-08-16，寅时，女
\`\`\`

### 测试五行分析
\`\`\`
分析一下这个八字的五行：2000年8月16日，寅时，女性
\`\`\`

---

## 🐛 常见问题排查

### PyPI相关

**问题1：安装失败**
\`\`\`bash
# 检查包信息
pip show mingli-mcp

# 详细安装日志
pip install mingli-mcp -v
\`\`\`

**问题2：命令找不到**
\`\`\`bash
# 检查安装位置
pip show mingli-mcp | grep Location

# 检查PATH
echo $PATH

# 尝试直接调用
python -m mingli_mcp
\`\`\`

### Cloudflare相关

**问题1：域名无法访问**
\`\`\`bash
# 检查DNS
nslookup mcp.lee.locker

# 检查Cloudflare隧道状态
cloudflared tunnel info mingli-mcp

# 检查本地服务
curl http://localhost:8080/health
\`\`\`

**问题2：MCP请求失败**
\`\`\`bash
# 查看隧道日志
cloudflared tunnel run mingli-mcp --loglevel debug

# 查看MCP服务日志
export LOG_LEVEL=DEBUG
python mingli_mcp.py
\`\`\`

---

## 📊 监控建议

### 1. PyPI下载统计
访问：https://pypistats.org/packages/mingli-mcp

### 2. Cloudflare分析
访问：https://dash.cloudflare.com → Analytics

### 3. 本地日志
\`\`\`bash
# MCP服务日志
tail -f /path/to/logs/mingli-mcp.log

# Cloudflare隧道日志
journalctl -u cloudflared -f
\`\`\`

---

## ✅ 检查通过标准

部署成功应满足：

- ✅ PyPI包可正常安装
- ✅ Cloudflare域名可访问（HTTPS）
- ✅ 健康检查返回 `{"status": "healthy"}`
- ✅ MCP工具列表正常返回
- ✅ 在Coze中配置成功
- ✅ 命理系统调用正常

---

**生成于：** $(date +"%Y-%m-%d %H:%M:%S")
