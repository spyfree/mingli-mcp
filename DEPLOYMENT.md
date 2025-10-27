# 部署指南

## 📦 方案A：发布到PyPI（推荐）

### 1. 准备工作

```bash
# 安装构建工具
pip install build twine

# 清理旧的构建文件
rm -rf dist/ build/ *.egg-info
```

### 2. 构建包

```bash
# 构建分发包
python -m build

# 会生成：
# dist/mingli-mcp-1.0.0.tar.gz
# dist/mingli_mcp-1.0.0-py3-none-any.whl
```

### 3. 测试本地安装

```bash
# 在新环境中测试
python -m venv test_env
source test_env/bin/activate
pip install dist/mingli_mcp-1.0.0-py3-none-any.whl

# 测试命令
mingli-mcp --help

# 清理
deactivate
rm -rf test_env
```

### 4. 发布到PyPI

```bash
# 上传到测试PyPI（可选）
twine upload --repository testpypi dist/*

# 上传到正式PyPI
twine upload dist/*
```

### 5. 在Coze中使用

发布后，在Coze的"自定义MCP扩展"中配置：

```json
{
  "mcpServers": {
    "mingli": {
      "command": "uvx",
      "args": ["mingli-mcp@1.0.0"],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

或使用pip方式：

```json
{
  "mcpServers": {
    "mingli": {
      "command": "python",
      "args": ["-m", "pip", "install", "mingli-mcp", "&&", "mingli-mcp"],
      "env": {}
    }
  }
}
```

---

## 🌐 方案B：HTTP服务（适合多平台）

### 1. 实现HTTP传输层

创建 `transports/http_transport.py`：

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from .base_transport import BaseTransport

class HttpTransport(BaseTransport):
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self.app = FastAPI(title="Mingli MCP Server")
        self._setup_routes()
    
    def _setup_routes(self):
        @self.app.post("/mcp")
        async def handle_mcp(request: Request):
            data = await request.json()
            response = self.message_handler(data)
            return JSONResponse(response)
        
        @self.app.get("/health")
        async def health():
            return {"status": "ok"}
    
    def start(self):
        uvicorn.run(self.app, host=self.host, port=self.port)
    
    def send_message(self, message):
        # HTTP模式不需要主动发送
        pass
    
    def receive_message(self):
        # HTTP模式由FastAPI处理
        pass
```

### 2. 添加HTTP依赖

在 `requirements.txt` 添加：

```txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
```

### 3. 启动HTTP服务

```bash
# 修改 config.py
TRANSPORT_TYPE = "http"
HTTP_HOST = "0.0.0.0"
HTTP_PORT = 8080

# 启动服务
python mingli_mcp.py
```

### 4. 在Coze中配置HTTP MCP

```json
{
  "mcpServers": {
    "mingli": {
      "url": "https://your-domain.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

### 5. 部署到云端

可选择：
- Railway.app（免费额度）
- Render.com（免费额度）
- Fly.io（免费额度）
- 阿里云/腾讯云

**Dockerfile 示例**：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV TRANSPORT_TYPE=http
ENV HTTP_HOST=0.0.0.0
ENV HTTP_PORT=8080

EXPOSE 8080

CMD ["python", "mingli_mcp.py"]
```

---

## 🔧 方案C：私有PyPI服务器（企业内网）

如果不想公开发布，可以搭建私有PyPI：

### 使用 devpi

```bash
# 安装devpi
pip install devpi-server devpi-web devpi-client

# 启动服务器
devpi-server --start --init

# 创建索引
devpi use http://localhost:3141
devpi login root --password=''
devpi index -c dev bases=root/pypi

# 上传包
devpi use root/dev
devpi upload
```

### 在Coze中使用私有源

```json
{
  "mcpServers": {
    "mingli": {
      "command": "pip",
      "args": [
        "install", 
        "--index-url", "http://your-devpi-server:3141/root/dev/+simple/",
        "mingli-mcp",
        "&&",
        "mingli-mcp"
      ]
    }
  }
}
```

---

## 📊 方案对比

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| **PyPI包** | 标准、易用、支持Coze | 需要公开代码 | 开源项目 |
| **HTTP服务** | 灵活、支持所有平台 | 需要服务器 | 商业项目 |
| **私有PyPI** | 不公开代码、内网可用 | 需维护服务器 | 企业内部 |

---

## 🎯 推荐实施路线

### 阶段1：PyPI发布（1-2小时）
1. ✅ 完善 `pyproject.toml`
2. ✅ 构建和测试
3. ✅ 发布到PyPI
4. ✅ 在Coze测试

### 阶段2：HTTP支持（2-3小时）
1. 实现 `http_transport.py`
2. 添加FastAPI依赖
3. 本地测试HTTP模式
4. 部署到云端

### 阶段3：文档完善（1小时）
1. 更新README添加部署说明
2. 创建Coze使用教程
3. 添加API文档

---

## 🧪 测试清单

### PyPI包测试
- [ ] 本地构建成功
- [ ] 虚拟环境安装成功
- [ ] 命令行工具可用
- [ ] 在Coze中配置成功
- [ ] 在Coze中调用成功

### HTTP服务测试
- [ ] 本地启动成功
- [ ] 健康检查接口正常
- [ ] MCP请求响应正常
- [ ] 云端部署成功
- [ ] 远程调用成功

---

## 📞 常见问题

### Q1: Coze一直显示"扩展加载失败"
**A**: 检查：
1. Python版本兼容性（>=3.8）
2. 依赖是否完整安装
3. 日志中的错误信息

### Q2: HTTP服务如何添加认证？
**A**: 在FastAPI中添加依赖注入：

```python
from fastapi import Depends, HTTPException, Header

async def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(401)
    # 验证token
    return True

@app.post("/mcp", dependencies=[Depends(verify_token)])
async def handle_mcp(request: Request):
    ...
```

### Q3: 如何监控服务运行状态？
**A**: 添加监控端点：

```python
@app.get("/metrics")
async def metrics():
    return {
        "requests_total": request_counter,
        "requests_success": success_counter,
        "requests_failed": error_counter,
        "uptime_seconds": time.time() - start_time
    }
```

---

## 🔐 安全建议

1. **环境变量**: 敏感配置使用环境变量
2. **API认证**: 生产环境必须添加认证
3. **HTTPS**: 使用HTTPS加密传输
4. **限流**: 添加请求频率限制
5. **日志**: 记录关键操作但不记录敏感信息

---

## 📚 参考资源

- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [Coze MCP文档](https://www.coze.cn/docs/guides/mcp)
- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
