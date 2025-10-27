# Coze 扣子平台集成指南

## 🎯 方案概述

由于Coze运行在云端沙箱环境，有两种推荐的集成方案：

### 方案1：HTTP服务（推荐⭐⭐⭐⭐⭐）

**优点**：
- ✅ 最稳定可靠
- ✅ 不依赖Coze沙箱环境
- ✅ 便于监控和维护
- ✅ 支持认证和限流

**缺点**：
- ⚠️ 需要云端服务器
- ⚠️ 需要公网域名（或使用内网穿透）

### 方案2：PyPI包

**优点**：
- ✅ 易于分发
- ✅ 符合Python生态标准

**缺点**：
- ⚠️ Coze沙箱网络可能受限
- ⚠️ 安装依赖可能较慢
- ⚠️ 需要发布到PyPI

## 🚀 方案1：HTTP服务部署（推荐）

### 步骤1：启动本地HTTP服务

```bash
cd /Users/lix18854/Documents/code/ziwei_mcp

# 设置为HTTP模式
export TRANSPORT_TYPE=http
export HTTP_PORT=8080

# 启动服务
source venv/bin/activate
python mingli_mcp.py
```

服务启动后会监听在 `http://localhost:8080`

### 步骤2：测试本地服务

```bash
# 健康检查
curl http://localhost:8080/health

# 测试MCP请求
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```

### 步骤3：部署到云端

#### 选项A：Railway.app（免费，推荐）

1. 注册 https://railway.app
2. 连接GitHub仓库
3. 添加环境变量：
   ```
   TRANSPORT_TYPE=http
   HTTP_PORT=8080
   ```
4. Railway会自动部署，生成公网URL

#### 选项B：Render.com（免费）

1. 注册 https://render.com
2. 创建Web Service
3. 连接GitHub仓库
4. 设置启动命令：
   ```bash
   TRANSPORT_TYPE=http python mingli_mcp.py
   ```

#### 选项C：内网穿透（开发测试用）

使用 ngrok/cpolar/frp 等工具：

```bash
# 安装ngrok
brew install ngrok

# 启动内网穿透
ngrok http 8080
```

会生成类似 `https://abc123.ngrok.io` 的公网地址

### 步骤4：在Coze配置

进入Coze控制台 → 扩展 → 添加自定义扩展

**配置示例**：

```json
{
  "mcpServers": {
    "mingli": {
      "url": "https://your-domain.com/mcp",
      "headers": {
        "Content-Type": "application/json"
      }
    }
  }
}
```

**说明**：
- `url`: 你的HTTP服务地址 + `/mcp` 路径
- 如果设置了API密钥，添加：
  ```json
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_API_KEY"
  }
  ```

### 步骤5：在Coze使用

创建Bot，在Bot设置中：
1. 开启"扩展"功能
2. 勾选"mingli"扩展
3. 测试对话

**测试命令**：
```
帮我排一个紫微斗数盘：2000年8月16日，寅时，女性
```

```
帮我看看八字：2000-08-16，寅时，女
```

## 🔐 安全配置

### 启用API密钥认证

在 `.env` 文件中设置：

```bash
HTTP_API_KEY=your-secret-key-here
```

或在启动时设置：

```bash
export HTTP_API_KEY=your-secret-key
python mingli_mcp.py
```

在Coze配置中添加认证头：

```json
{
  "mcpServers": {
    "mingli": {
      "url": "https://your-domain.com/mcp",
      "headers": {
        "Content-Type": "application/json",
        "Authorization": "Bearer your-secret-key-here"
      }
    }
  }
}
```

## 📊 监控和调试

### 查看日志

HTTP服务会输出详细日志：

```bash
# 设置DEBUG级别
export LOG_LEVEL=DEBUG
python mingli_mcp.py
```

### 健康检查端点

```bash
curl http://your-domain.com/health
```

响应示例：
```json
{
  "status": "healthy",
  "transport": "http",
  "systems": ["ziwei", "bazi"]
}
```

### API文档

FastAPI自动生成文档，访问：

- Swagger UI: `http://your-domain.com/docs`
- ReDoc: `http://your-domain.com/redoc`

## 🐛 常见问题

### Q1: Coze提示"扩展连接失败"

**检查**：
1. 服务是否正常运行
2. URL是否正确（必须是HTTPS，包含 `/mcp` 路径）
3. 防火墙是否允许访问
4. API密钥是否正确

**调试**：
```bash
# 测试MCP端点
curl -X POST https://your-domain.com/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_KEY" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

### Q2: 请求超时

**原因**：
- 服务器性能不足
- 依赖包加载慢

**解决**：
1. 增加服务器配置
2. 使用持久化部署（避免冷启动）
3. 预加载模型

### Q3: CORS错误

HTTP传输已配置CORS允许所有来源：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📈 性能优化

### 1. 使用生产级服务器

```bash
# 安装gunicorn
pip install gunicorn

# 启动多worker
gunicorn mingli_mcp:app -w 4 -k uvicorn.workers.UvicornWorker
```

### 2. 添加缓存

对频繁请求的结果添加缓存：

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_chart(date, time_index, gender):
    # 排盘逻辑
    pass
```

### 3. 限流

使用 slowapi 限制请求频率：

```bash
pip install slowapi
```

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/mcp")
@limiter.limit("10/minute")
async def handle_mcp(request: Request):
    ...
```

## 🎯 下一步

### 短期（完成HTTP部署）
- [ ] 本地测试HTTP服务
- [ ] 选择云平台（Railway/Render）
- [ ] 部署到云端
- [ ] 在Coze配置测试

### 中期（功能完善）
- [ ] 添加请求日志分析
- [ ] 性能监控仪表盘
- [ ] 自动化部署流程
- [ ] 多环境支持（开发/测试/生产）

### 长期（扩展集成）
- [ ] 支持Dify等其他平台
- [ ] WebSocket实时推送
- [ ] 批量处理接口
- [ ] 数据分析报表

## 📞 技术支持

遇到问题？
1. 查看日志输出
2. 测试健康检查端点
3. 查看API文档（/docs）
4. 检查环境变量配置

---

**更新日期**: 2025-10-27  
**版本**: 1.0.0
