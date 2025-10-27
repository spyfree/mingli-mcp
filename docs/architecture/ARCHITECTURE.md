# 架构设计文档

## 📐 架构概览

本项目采用**三层架构 + 插件化设计**，实现了高度可扩展的命理MCP服务。

```
┌─────────────────────────────────────────────────────┐
│                  MCP客户端 (Cursor)                  │
└───────────────────┬─────────────────────────────────┘
                    │ JSON-RPC
┌───────────────────┴─────────────────────────────────┐
│              传输层 (Transport Layer)                │
│  ┌─────────────┬─────────────┬──────────────────┐  │
│  │   stdio     │    HTTP     │   WebSocket      │  │
│  │  (默认)     │  (预留)     │    (预留)        │  │
│  └─────────────┴─────────────┴──────────────────┘  │
└───────────────────┬─────────────────────────────────┘
                    │
┌───────────────────┴─────────────────────────────────┐
│           MCP服务层 (mingli_mcp.py)                  │
│  - 初始化处理                                        │
│  - 工具注册                                          │
│  - 请求路由                                          │
│  - 响应格式化                                        │
└───────────────────┬─────────────────────────────────┘
                    │
┌───────────────────┴─────────────────────────────────┐
│            系统注册中心 (systems/)                    │
│  ┌──────────────────────────────────────────────┐  │
│  │  register_system()  │  get_system()          │  │
│  └──────────────────────────────────────────────┘  │
└─────┬─────────────────┬─────────────────┬──────────┘
      │                 │                 │
┌─────┴──────┐  ┌──────┴──────┐  ┌──────┴─────────┐
│   紫微斗数   │  │    八字      │  │   西方占星     │
│ (ZiweiSystem)│  │ (BaziSystem) │  │(AstroSys 预留)│
│   ✅ 已实现   │  │  🔄 预留     │  │   🔄 预留      │
└─────┬──────┘  └──────┬──────┘  └──────┬─────────┘
      │                │                │
      └────────────────┴────────────────┘
                       │
           ┌───────────┴───────────┐
           │   核心抽象层 (core/)  │
           │  BaseFortuneSystem    │
           │  BirthInfo            │
           │  ChartResult          │
           └───────────────────────┘
```

## 🧩 核心组件

### 1. 核心抽象层 (core/)

#### BaseFortuneSystem
所有命理系统的抽象基类，定义统一接口：

```python
class BaseFortuneSystem(ABC):
    @abstractmethod
    def get_system_name() -> str
    
    @abstractmethod
    def get_chart(birth_info) -> Dict
    
    @abstractmethod
    def get_fortune(birth_info, query_date) -> Dict
    
    @abstractmethod
    def analyze_palace(birth_info, palace_name) -> Dict
```

**设计优势**：
- 统一接口：所有系统遵循相同规范
- 多态性：可以互换使用不同系统
- 易于测试：统一的测试接口

#### BirthInfo
生辰信息数据模型，包含验证逻辑：

```python
@dataclass
class BirthInfo:
    date: str  # YYYY-MM-DD
    time_index: int  # 0-12
    gender: str  # "男"/"女"
    calendar: str  # "solar"/"lunar"
    is_leap_month: bool
```

#### ChartResult
排盘结果统一格式，支持多种输出：

```python
@dataclass
class ChartResult:
    system: str
    basic_info: Dict
    palaces: List[Dict]
    metadata: Dict
    
    def to_markdown() -> str
    def to_dict() -> Dict
```

### 2. 传输层 (transports/)

#### BaseTransport
传输层抽象基类，支持多种传输协议：

```python
class BaseTransport(ABC):
    def set_message_handler(handler: Callable)
    
    @abstractmethod
    def start()
    
    @abstractmethod
    def send_message(message: Dict)
    
    @abstractmethod
    def receive_message() -> Dict
```

#### StdioTransport (已实现)
标准输入输出传输，用于Cursor等IDE：
- JSON-RPC over stdio
- 自动处理消息序列化/反序列化
- 错误处理和日志记录

#### 预留扩展
```python
# HttpTransport (预留)
class HttpTransport(BaseTransport):
    def __init__(self, host, port):
        # FastAPI/Flask实现HTTP服务
        pass

# WebSocketTransport (预留)
class WebSocketTransport(BaseTransport):
    def __init__(self, host, port):
        # WebSocket实时通信
        pass
```

### 3. 系统注册中心 (systems/)

**插件化架构**：
```python
# 自动注册机制
_SYSTEMS: Dict[str, Type[BaseFortuneSystem]] = {}

def register_system(name: str, system_class: Type):
    _SYSTEMS[name] = system_class

def get_system(name: str) -> BaseFortuneSystem:
    return _SYSTEMS[name]()

# 自动发现并注册
try:
    from .ziwei import ZiweiSystem
    register_system('ziwei', ZiweiSystem)
except ImportError:
    pass
```

**优势**：
- 自动发现：新系统自动注册
- 延迟加载：只在需要时加载
- 容错性：单个系统失败不影响其他

### 4. 紫微斗数系统 (systems/ziwei/)

#### ZiweiSystem
紫微斗数核心实现，基于py-iztro库：

```python
class ZiweiSystem(BaseFortuneSystem):
    def get_chart(birth_info):
        # 使用py-iztro生成排盘
        astro = Astro()
        astrolabe = astro.by_solar(...)
        return formatter.format_chart(astrolabe)
    
    def get_fortune(birth_info, query_date):
        # 查询运势（大限、流年等）
        horoscope = astrolabe.horoscope(query_date)
        return formatter.format_fortune(horoscope)
    
    def analyze_palace(birth_info, palace_name):
        # 分析特定宫位
        chart = self.get_chart(birth_info)
        palace = find_palace(chart, palace_name)
        return formatter.format_palace_analysis(palace)
```

#### ZiweiFormatter
结果格式化器，支持多种输出：

```python
class ZiweiFormatter:
    def format_chart(astrolabe) -> Dict
    def format_chart_markdown(chart) -> str
    def format_fortune(horoscope, query_date) -> Dict
    def format_fortune_markdown(fortune) -> str
    def format_palace_analysis(palace, basic_info) -> Dict
    def format_palace_analysis_markdown(analysis) -> str
```

### 5. MCP服务层 (mingli_mcp.py)

#### MingliMCPServer
MCP协议实现：

```python
class MingliMCPServer:
    def handle_request(request: Dict) -> Dict:
        method = request['method']
        
        if method == 'initialize':
            return initialize_response()
        
        elif method == 'tools/list':
            return list_all_tools()
        
        elif method == 'tools/call':
            tool_name = request['params']['name']
            return call_tool(tool_name, arguments)
```

#### 工具定义
每个工具对应一个命理功能：

```json
{
  "name": "get_ziwei_chart",
  "description": "获取紫微斗数排盘...",
  "inputSchema": {
    "type": "object",
    "properties": {
      "date": {"type": "string"},
      "time_index": {"type": "integer"},
      "gender": {"type": "string"}
    }
  }
}
```

## 🔄 请求处理流程

### 排盘请求流程

```
1. Cursor发送工具调用请求
   ↓
2. StdioTransport接收JSON-RPC消息
   ↓
3. MingliMCPServer.handle_request()
   ↓
4. 解析tool_name和arguments
   ↓
5. get_system('ziwei') 获取系统实例
   ↓
6. ZiweiSystem.get_chart(birth_info)
   ↓
7. 调用py-iztro: astro.by_solar(...)
   ↓
8. ZiweiFormatter.format_chart()
   ↓
9. 转换为markdown或json
   ↓
10. 封装为MCP响应
    ↓
11. StdioTransport发送响应
    ↓
12. Cursor显示结果
```

### 错误处理流程

```
异常发生
   ↓
被系统层捕获 (ZiweiSystem)
   ↓
转换为RuntimeError
   ↓
被MCP服务层捕获 (MingliMCPServer)
   ↓
转换为JSON-RPC错误响应
   ↓
返回给客户端
```

## 🚀 扩展指南

### 添加新命理系统

#### 步骤1: 创建系统目录
```bash
mkdir systems/bazi
touch systems/bazi/__init__.py
touch systems/bazi/bazi_system.py
touch systems/bazi/formatter.py
```

#### 步骤2: 实现系统类
```python
# systems/bazi/bazi_system.py
from core.base_system import BaseFortuneSystem

class BaziSystem(BaseFortuneSystem):
    def get_system_name(self) -> str:
        return "八字"
    
    def get_chart(self, birth_info):
        # 实现八字排盘逻辑
        year_pillar = self._calc_year_pillar(birth_info['date'])
        month_pillar = self._calc_month_pillar(...)
        # ...
        return {
            'system': '八字',
            'basic_info': {...},
            'pillars': [year_pillar, month_pillar, ...],
        }
    
    # 实现其他必需方法...
```

#### 步骤3: 注册系统
```python
# systems/__init__.py
try:
    from .bazi import BaziSystem
    register_system('bazi', BaziSystem)
except ImportError:
    pass
```

#### 步骤4: 添加MCP工具
```python
# mingli_mcp.py
def _handle_tools_list(self, request_id):
    tools.append({
        "name": "get_bazi_chart",
        "description": "获取八字排盘信息",
        "inputSchema": {...}
    })
```

### 添加新传输方式

#### HTTP传输示例
```python
# transports/http_transport.py
from fastapi import FastAPI
from .base_transport import BaseTransport

class HttpTransport(BaseTransport):
    def __init__(self, host: str, port: int):
        super().__init__()
        self.app = FastAPI()
        self.host = host
        self.port = port
        self._setup_routes()
    
    def _setup_routes(self):
        @self.app.post("/mcp")
        async def handle_mcp_request(request: Dict):
            return self.handle_message(request)
    
    def start(self):
        import uvicorn
        uvicorn.run(self.app, host=self.host, port=self.port)
```

使用：
```python
# config.py
TRANSPORT_TYPE = 'http'

# mingli_mcp.py
if transport_type == 'http':
    self.transport = HttpTransport(
        config.HTTP_HOST, 
        config.HTTP_PORT
    )
```

## 📊 数据流图

### 紫微排盘数据流

```
用户输入 → BirthInfo
   ↓
{
  date: "2000-08-16",
  time_index: 2,
  gender: "女",
  calendar: "solar"
}
   ↓
ZiweiSystem.get_chart()
   ↓
py-iztro: Astro.by_solar()
   ↓
AstrolabeModel {
  solar_date, lunar_date,
  palaces: [Palace * 12],
  ...
}
   ↓
ZiweiFormatter.format_chart()
   ↓
{
  system: "紫微斗数",
  basic_info: {...},
  palaces: [{...}, ...],
  metadata: {...}
}
   ↓
ZiweiFormatter.format_chart_markdown()
   ↓
Markdown文本输出
```

## 🔐 安全性考虑

1. **输入验证**：
   - BirthInfo的`__post_init__`自动验证
   - validators模块提供额外验证

2. **错误隔离**：
   - 每个系统独立错误处理
   - 不会因单个系统失败而全局崩溃

3. **资源限制**：
   - 无状态设计，避免内存泄漏
   - 每次请求独立处理

## 📈 性能优化

1. **延迟加载**：
   - 系统只在首次使用时加载
   - py-iztro库按需导入

2. **无状态设计**：
   - 无缓存开销
   - 易于水平扩展

3. **轻量通信**：
   - JSON-RPC最小化传输
   - stdio零网络延迟

## 🧪 测试策略

### 单元测试
```python
# tests/test_ziwei.py
def test_ziwei_chart():
    ziwei = get_system('ziwei')
    birth_info = {...}
    chart = ziwei.get_chart(birth_info)
    assert chart['system'] == '紫微斗数'
    assert len(chart['palaces']) == 12
```

### 集成测试
```python
# tests/test_mcp.py
def test_mcp_workflow():
    server = MingliMCPServer()
    request = {
        "method": "tools/call",
        "params": {...}
    }
    response = server.handle_request(request)
    assert 'result' in response
```

## 📚 参考资料

- [MCP协议规范](https://modelcontextprotocol.io/)
- [py-iztro文档](https://github.com/x-haose/py-iztro)
- [iztro官方文档](https://ziwei.pro/)

---

**本架构文档持续更新中** 🚀
