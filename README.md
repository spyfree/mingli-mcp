# 命理MCP服务 (Mingli MCP Server)

一个支持多种命理系统（紫微斗数、八字、占星等）的 Model Context Protocol (MCP) 服务器，专为 AI 工具（如 Cursor IDE）设计。

## ✨ 特性

### 🎯 核心特性
- ✅ **多命理系统支持**: 采用插件化架构，轻松扩展新的命理系统
  - ✅ 紫微斗数（已实现）
  - ✅ 八字（已实现）⭐ **新增**
  - 🔄 西方占星（预留接口）
- ✅ **多传输方式**: 支持stdio、HTTP、WebSocket等多种传输协议
- ✅ **MCP标准兼容**: 完全兼容 MCP 协议规范
- ✅ **易于扩展**: 清晰的抽象层设计，添加新系统只需3步

### 🔮 紫微斗数功能
- ✅ **完整排盘**: 十二宫、主星、辅星、杂耀、四化等
- ✅ **运势查询**: 大限、流年、流月、流日、流时
- ✅ **宫位分析**: 深度分析特定宫位的星曜配置
- ✅ **多种历法**: 支持阳历和农历输入
- ✅ **格式化输出**: JSON和Markdown两种输出格式

### 🎴 八字功能 ⭐ **新增**
- ✅ **四柱排盘**: 年月日时四柱、天干地支详细信息
- ✅ **十神分析**: 比肩、劫财、食神、伤官、偏财、正财、七杀、正官、偏印、正印
- ✅ **五行分析**: 金木水火土分数、百分比、平衡度
- ✅ **地支藏干**: 详细的地支藏干信息
- ✅ **运势查询**: 大运、流年分析
- ✅ **缺失分析**: 自动识别五行缺失并给出建议
- ✅ **多种历法**: 支持阳历和农历输入

## 📋 可用工具

### 1. get_ziwei_chart
获取紫微斗数完整排盘信息

**参数**:
- `date` (string, 必需): 出生日期 YYYY-MM-DD，如 "2000-08-16"
- `time_index` (integer, 必需): 时辰序号 0-12
  - 0=早子时(23-01), 1=丑时(01-03), 2=寅时(03-05), 3=卯时(05-07)
  - 4=辰时(07-09), 5=巳时(09-11), 6=午时(11-13), 7=未时(13-15)
  - 8=申时(15-17), 9=酉时(17-19), 10=戌时(19-21), 11=亥时(21-23)
  - 12=晚子时(23-01)
- `gender` (string, 必需): 性别 "男" 或 "女"
- `calendar` (string, 可选): 历法 "solar"(阳历) 或 "lunar"(农历), 默认 "solar"
- `is_leap_month` (boolean, 可选): 是否闰月，默认 false
- `format` (string, 可选): 输出格式 "json" 或 "markdown", 默认 "markdown"

**示例**:
```json
{
  "date": "2000-08-16",
  "time_index": 2,
  "gender": "女",
  "calendar": "solar"
}
```

### 2. get_ziwei_fortune
获取紫微斗数运势信息

**参数**:
- `birth_date` (string, 必需): 出生日期
- `time_index` (integer, 必需): 时辰序号
- `gender` (string, 必需): 性别
- `calendar` (string, 可选): 历法类型
- `query_date` (string, 可选): 查询日期，不填则为今天
- `format` (string, 可选): 输出格式

### 3. analyze_ziwei_palace
分析紫微斗数特定宫位

**参数**:
- `birth_date` (string, 必需): 出生日期
- `time_index` (integer, 必需): 时辰序号
- `gender` (string, 必需): 性别
- `palace_name` (string, 必需): 宫位名称，可选值：
  - 命宫、兄弟、夫妻、子女、财帛、疾厄
  - 迁移、仆役、官禄、田宅、福德、父母
- `calendar` (string, 可选): 历法类型
- `format` (string, 可选): 输出格式

### 4. list_fortune_systems
列出所有可用的命理系统

### 5. get_bazi_chart ⭐ **新增**
获取八字（四柱）排盘信息

**参数**:
- `date` (string, 必需): 出生日期 YYYY-MM-DD
- `time_index` (integer, 必需): 时辰序号 0-12
- `gender` (string, 必需): 性别 "男" 或 "女"
- `calendar` (string, 可选): 历法 "solar"(阳历) 或 "lunar"(农历), 默认 "solar"
- `is_leap_month` (boolean, 可选): 是否闰月，默认 false
- `format` (string, 可选): 输出格式 "json" 或 "markdown", 默认 "markdown"

**示例**:
```json
{
  "date": "2000-08-16",
  "time_index": 2,
  "gender": "女"
}
```

**输出包含**:
- 四柱八字（年月日时）
- 天干地支详细信息
- 十神分析（比肩、劫财等）
- 五行分数统计
- 地支藏干信息
- 生肖、日主等基本信息

### 6. get_bazi_fortune ⭐ **新增**
获取八字运势信息

**参数**:
- `birth_date` (string, 必需): 出生日期
- `time_index` (integer, 必需): 时辰序号
- `gender` (string, 必需): 性别
- `calendar` (string, 可选): 历法类型
- `query_date` (string, 可选): 查询日期，不填则为今天
- `format` (string, 可选): 输出格式

**输出包含**:
- 当前年龄
- 大运信息（年龄范围、干支）
- 流年信息（年份、干支、生肖）
- 本命八字

### 7. analyze_bazi_element ⭐ **新增**
分析八字五行强弱

**参数**:
- `birth_date` (string, 必需): 出生日期
- `time_index` (integer, 必需): 时辰序号
- `gender` (string, 必需): 性别
- `calendar` (string, 可选): 历法类型
- `format` (string, 可选): 输出格式

**输出包含**:
- 日主及其五行属性
- 五行分数和百分比
- 最旺/最弱五行
- 缺失五行
- 平衡度评价
- 补救建议

## 🚀 快速开始

### 在线体验
- **Smithery 部署**: [https://server.smithery.ai/@spyfree/mingli-mcp/mcp](https://server.smithery.ai/@spyfree/mingli-mcp/mcp)
- 添加到 Cursor: [![Install MCP Server](https://img.shields.io/badge/Cursor-Add+MCP+Server-blue?logo=cursor)](https://cursor.com/install-mcp?name=mingli&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyJtaW5nbGktbWNwIl19)
- 添加到 Claude Code: `claude mcp add mingli -- uvx mingli-mcp`
- 添加到 OpenAI CodeX: `codex mcp add mingli -- uvx mingli-mcp`

---

## 📦 安装方式

### 方式1: uvx (推荐)

使用 `uvx` 是最简单的安装方式，无需手动管理依赖：

在 `~/.cursor/mcp.json` 或对应IDE的MCP配置文件中添加：

```json
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
```

### 方式2: Docker

使用 Docker 部署，适合服务器环境或需要隔离的场景：

```bash
# 下载配置文件
mkdir -p /opt/mingli-mcp
cd /opt/mingli-mcp
wget https://raw.githubusercontent.com/spyfree/mingli-mcp/main/docker-compose.yml

# 启动服务
docker-compose up -d
```

然后在MCP配置中使用HTTP连接：

```json
{
  "mcpServers": {
    "mingli": {
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

### 方式3: 从源码安装

适合开发者或需要自定义的场景：

## 🛠️ 从源码安装

### 环境要求
- Python 3.8+
- Cursor IDE 或其他支持MCP的工具

### 1. 克隆项目
```bash
cd /Users/lix18854/Documents/code
# 项目已在 ziwei_mcp 目录中
cd ziwei_mcp
```

### 2. 创建虚拟环境（推荐）
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

#### 基础安装（stdio模式，推荐）
```bash
pip install -r requirements.txt
```

#### 或完整安装（包含HTTP传输支持）
```bash
pip install -r requirements-http.txt
# 或使用 pip install .[http]
```

> **注意**: stdio模式无需任何额外配置即可使用，推荐日常使用。HTTP模式仅在需要Docker部署或服务器环境时使用。

### 4. 配置环境变量（可选）
```bash
cp examples/config/.env.example .env
# 编辑 .env 文件根据需要调整配置
```

### 5. 测试运行
```bash
chmod +x mingli_mcp.py
python mingli_mcp.py
```

### 6. 配置 Cursor MCP

编辑或创建 `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "mingli": {
      "command": "/Users/lix18854/Documents/code/ziwei_mcp/venv/bin/python",
      "args": ["/Users/lix18854/Documents/code/ziwei_mcp/mingli_mcp.py"],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

> **注意**: 请根据实际路径调整 `command` 和 `args`

### 7. 重启 Cursor
重启 Cursor IDE 以加载新的 MCP 配置。

## 📁 项目结构

```
ziwei_mcp/
├── mingli_mcp.py              # MCP服务器主入口
├── config.py                  # 配置管理
├── requirements.txt           # Python依赖
├── pyproject.toml            # 项目配置
├── .gitignore                # Git忽略文件
├── README.md                 # 项目文档
│
├── core/                      # 核心抽象层
│   ├── __init__.py
│   ├── base_system.py        # 命理系统抽象基类
│   ├── birth_info.py         # 生辰信息数据模型
│   └── chart_result.py       # 排盘结果数据模型
│
├── transports/                # 传输层（支持多种传输方式）
│   ├── __init__.py
│   ├── base_transport.py     # 传输层抽象基类
│   └── stdio_transport.py    # stdio传输实现（默认）
│
├── systems/                   # 命理系统实现
│   ├── __init__.py           # 系统注册中心
│   ├── ziwei/                # 紫微斗数（已实现）
│   │   ├── __init__.py
│   │   ├── ziwei_system.py  # 系统实现
│   │   └── formatter.py     # 结果格式化
│   ├── bazi/                 # 八字（已实现）
│   │   ├── __init__.py
│   │   ├── bazi_system.py   # 系统实现
│   │   └── formatter.py     # 结果格式化
│   └── astrology/            # 占星（预留）
│       └── __init__.py
│
├── utils/                     # 工具函数
│   ├── __init__.py
│   ├── validators.py         # 参数验证
│   └── formatters.py         # 响应格式化
│
├── docs/                      # 文档
│   ├── README.md             # 文档索引
│   ├── guides/               # 用户指南
│   ├── deployment/           # 部署文档
│   ├── architecture/         # 架构设计
│   └── development/          # 开发文档
│
├── examples/                  # 示例配置
│   └── config/               # 配置文件示例
│       ├── .env.example
│       ├── codex_config.toml.example
│       └── cursor_mcp_config.example.json
│
├── scripts/                   # 脚本工具
│   ├── tests/                # 测试脚本
│   └── check_ready_to_publish.sh
│
└── tests/                     # 单元测试
    └── __init__.py
```

## 🚀 扩展新命理系统

本项目采用插件化架构，添加新命理系统只需3步：

### 步骤1: 创建系统类
在 `systems/` 下创建新目录，实现 `BaseFortuneSystem` 接口：

```python
# systems/bazi/bazi_system.py
from core.base_system import BaseFortuneSystem

class BaziSystem(BaseFortuneSystem):
    def get_system_name(self) -> str:
        return "八字"
    
    def get_chart(self, birth_info):
        # 实现八字排盘逻辑
        return {...}
    
    # 实现其他必需方法...
```

### 步骤2: 注册系统
在 `systems/__init__.py` 中注册：

```python
from .bazi import BaziSystem
register_system('bazi', BaziSystem)
```

### 步骤3: 添加MCP工具
在 `mingli_mcp.py` 的 `_handle_tools_list()` 中添加工具定义。

就这么简单！无需修改核心框架代码。

## 🔧 传输层扩展

当前默认使用 stdio 传输（适用于 Cursor）。未来可扩展：

### HTTP传输（预留）
```python
# transports/http_transport.py
class HttpTransport(BaseTransport):
    def __init__(self, host, port):
        # 实现HTTP服务器
        pass
```

### WebSocket传输（预留）
```python
# transports/ws_transport.py
class WebSocketTransport(BaseTransport):
    def __init__(self, host, port):
        # 实现WebSocket服务器
        pass
```

## 💡 最佳实践

### 在 AI 助手中使用

与AI助手（如Claude、Cursor等）对话时，可以直接使用自然语言查询：

**紫微斗数示例**：
- "帮我排一个紫微斗数盘：1990年5月20日，午时，男性"
- "查询这个人今年的运势如何"
- "分析他的财帛宫"
- "看看他适合什么行业"

**八字示例**：
- "帮我算八字：1985年3月15日，卯时，女性"  
- "分析一下她的五行缺什么"
- "看看她今年的大运"
- "什么五行的颜色适合她"

**农历支持**：
- "排盘：农历1995年7月初七，酉时，女性"
- "注意指定是农历"

### 提示词技巧

**详细查询**：
```
请帮我详细分析：
- 出生日期：2000年8月16日
- 出生时辰：寅时（早上5点）
- 性别：女
- 使用紫微斗数系统
- 重点看事业宫和财帛宫
```

**对比分析**：
```
请对比两个人的八字：
人A：1990年5月20日，午时，男
人B：1992年3月15日，辰时，女
看看他们的五行是否相配
```

**运势追踪**：
```
请记住这个人的信息：1988年10月1日，未时，男性
然后每个月帮我分析当月运势
```

---

## 📚 使用示例

### 在 Cursor 中使用

直接在对话中提问：

1. **获取紫微排盘**:
```
帮我排一个紫微斗数盘：2000年8月16日，寅时，女性
```

2. **查询运势**:
```
查询2000年8月16日寅时出生的女性，今天的紫微运势
```

3. **分析宫位**:
```
分析上面这个人的命宫
```

4. **八字五行分析**:
```
帮我看看这个人的五行：1995年7月10日，申时，男性
```

### 编程调用

```python
from systems import get_system

# 获取紫微系统
ziwei = get_system('ziwei')

# 准备生辰信息
birth_info = {
    'date': '2000-08-16',
    'time_index': 2,  # 寅时
    'gender': '女',
    'calendar': 'solar'
}

# 获取排盘
chart = ziwei.get_chart(birth_info)
print(chart)

# 获取运势
from datetime import datetime
fortune = ziwei.get_fortune(birth_info, datetime.now())
print(fortune)

# 分析宫位
palace = ziwei.analyze_palace(birth_info, '命宫')
print(palace)
```

## 🧪 测试

```bash
# 运行测试（待实现）
pytest tests/

# 测试单个系统
python -m systems.ziwei.ziwei_system
```

## 📝 依赖说明

- **iztro-py**: 紫微斗数核心库（纯 Python 实现，性能比 py-iztro 提升 10 倍）
- **python-dotenv**: 环境变量管理
- **python-dateutil**: 日期处理

## 🗺️ 未来规划

- [ ] 完善八字系统实现
- [ ] 添加西方占星系统
- [ ] 实现合盘功能
- [ ] HTTP/WebSocket传输层
- [ ] 命理知识库集成
- [ ] AI解读功能
- [ ] 更多运势分析维度

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

## 📄 许可证

MIT License

## 🙏 致谢

- [iztro](https://github.com/SylarLong/iztro) - 紫微斗数 JavaScript 库（原始算法来源）
- [iztro-py](https://github.com/spyfree/iztro-py) - 紫微斗数纯 Python 实现
- [MCP Protocol](https://modelcontextprotocol.io/) - Model Context Protocol 规范

---

**🔮 开始你的命理探索之旅！**
