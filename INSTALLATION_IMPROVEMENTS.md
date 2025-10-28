# 安装方式和文档改进

## 📅 更新时间
2025-10-28

## ✅ 完成的改进

参考项目：https://github.com/aahl/mcp-notify

### 1. 多种安装方式

#### 方式1: uvx (推荐)
✅ 最简单的安装方式，无需手动管理依赖

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

**优点**:
- 无需手动安装Python依赖
- 自动管理虚拟环境
- 一条命令即可运行
- 适合普通用户

#### 方式2: Docker
✅ 适合服务器环境和需要隔离的场景

**新增文件**:
- `Dockerfile` - Docker镜像构建文件
- `docker-compose.yml` - Docker Compose配置

**使用方法**:
```bash
# 下载配置
wget https://raw.githubusercontent.com/spyfree/mingli-mcp/main/docker-compose.yml

# 启动服务
docker-compose up -d
```

**配置**:
```json
{
  "mcpServers": {
    "mingli": {
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

**优点**:
- 环境隔离
- 易于部署到服务器
- 统一的运行环境
- 支持HTTP访问

#### 方式3: 从源码安装
✅ 适合开发者和需要自定义的场景

保留了原有的详细安装步骤，适合：
- 开发者进行开发和调试
- 需要自定义修改的用户
- 学习项目结构的用户

---

### 2. 快速开始

#### 一键安装链接
✅ 添加了便捷的安装链接

- **Cursor**: [![Install MCP Server](https://img.shields.io/badge/Cursor-Add+MCP+Server-blue?logo=cursor)](https://cursor.com/install-mcp?name=mingli&config=...)
- **Claude Code**: `claude mcp add mingli -- uvx mingli-mcp`
- **OpenAI CodeX**: `codex mcp add mingli -- uvx mingli-mcp`

**优点**:
- 一键添加到IDE
- 降低使用门槛
- 提升用户体验
- 类似于浏览器插件的安装体验

---

### 3. 最佳实践

#### 3.1 在 AI 助手中使用

✅ 添加了自然语言查询示例

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

#### 3.2 提示词技巧

✅ 添加了实用的提示词模板

**详细查询模板**：
```
请帮我详细分析：
- 出生日期：2000年8月16日
- 出生时辰：寅时（早上5点）
- 性别：女
- 使用紫微斗数系统
- 重点看事业宫和财帛宫
```

**对比分析模板**：
```
请对比两个人的八字：
人A：1990年5月20日，午时，男
人B：1992年3月15日，辰时，女
看看他们的五行是否相配
```

**运势追踪模板**：
```
请记住这个人的信息：1988年10月1日，未时，男性
然后每个月帮我分析当月运势
```

---

### 4. 新增配置文件

#### 4.1 smithery.yaml
✅ Smithery平台集成配置

```yaml
name: mingli-mcp
version: 1.0.3
description: 命理MCP服务 - 支持紫微斗数、八字等多种命理系统

tools:
  - name: get_ziwei_chart
    description: 获取紫微斗数完整排盘信息
  - name: get_bazi_chart
    description: 获取八字（四柱）排盘信息
  # ... 其他工具
```

**用途**:
- 支持在Smithery平台上托管
- 提供云端MCP服务
- 无需本地部署

#### 4.2 server.json
✅ MCP服务器元数据

```json
{
  "name": "mingli-mcp",
  "version": "1.0.3",
  "mcpServers": {
    "mingli": {
      "command": "uvx",
      "args": ["mingli-mcp"]
    }
  }
}
```

**用途**:
- MCP服务器标准配置
- 便于工具集成
- 提供服务元信息

#### 4.3 Dockerfile
✅ Docker镜像构建

```dockerfile
FROM python:3.11-slim
WORKDIR /app

# 安装依赖和应用
RUN pip install -e .

# 配置环境
ENV TRANSPORT_TYPE=http
ENV HTTP_PORT=8080

CMD ["mingli-mcp"]
```

**特点**:
- 基于Python 3.11-slim
- 支持HTTP传输
- 包含健康检查
- 自动重启

#### 4.4 docker-compose.yml
✅ Docker Compose编排

```yaml
services:
  mingli-mcp:
    build: .
    ports:
      - "8080:8080"
    environment:
      - HTTP_API_KEY=${HTTP_API_KEY:-}
      - ENABLE_RATE_LIMIT=${ENABLE_RATE_LIMIT:-true}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
```

**特点**:
- 环境变量配置
- 健康检查
- 自动重启
- 端口映射

---

### 5. 文档结构改进

#### 改进前
```
## 安装和配置
### 环境要求
### 1. 克隆项目
### 2. 创建虚拟环境
...
```

#### 改进后
```
## 🚀 快速开始
### 在线体验 (一键安装链接)

## 📦 安装方式
### 方式1: uvx (推荐)
### 方式2: Docker
### 方式3: 从源码安装

## 💡 最佳实践
### 在 AI 助手中使用
### 提示词技巧

## 📚 使用示例
```

**改进点**:
- 更清晰的层次结构
- 快速开始放在前面
- 多种安装选项
- 实用的最佳实践
- 使用表情符号增强可读性

---

## 📊 改进对比

| 项目 | 改进前 | 改进后 |
|------|--------|--------|
| 安装方式 | 1种（源码） | 3种（uvx、Docker、源码） |
| 快速开始 | 无 | 一键安装链接 |
| 最佳实践 | 无 | 完整示例和模板 |
| Docker支持 | 无 | 完整支持 |
| 文档结构 | 较平铺 | 层次清晰 |
| 配置文件 | 3个 | 7个 |

---

## 🎯 用户体验提升

### 对于普通用户
- ✅ 一键安装（uvx）
- ✅ 清晰的使用示例
- ✅ 自然语言提示词模板

### 对于开发者
- ✅ Docker部署方案
- ✅ 详细的源码安装步骤
- ✅ 清晰的项目结构说明

### 对于企业用户
- ✅ Docker Compose编排
- ✅ 环境变量配置
- ✅ 健康检查和自动重启

---

## 🚀 使用建议

### 普通用户推荐
使用 **方式1: uvx**，最简单快捷：
```json
{
  "mcpServers": {
    "mingli": {
      "command": "uvx",
      "args": ["mingli-mcp"]
    }
  }
}
```

### 服务器部署推荐
使用 **方式2: Docker**，稳定可靠：
```bash
wget https://raw.githubusercontent.com/spyfree/mingli-mcp/main/docker-compose.yml
docker-compose up -d
```

### 开发调试推荐
使用 **方式3: 从源码安装**，便于修改：
```bash
git clone https://github.com/spyfree/mingli-mcp.git
cd mingli-mcp
pip install -e ".[dev]"
```

---

## 📚 参考资料

- 参考项目: https://github.com/aahl/mcp-notify
- MCP协议: https://modelcontextprotocol.io/
- uvx文档: https://github.com/astral-sh/uv
- Docker文档: https://docs.docker.com/

---

## ✅ 总结

通过本次改进，mingli-mcp项目：

1. **降低使用门槛** - uvx一键安装
2. **增加部署选项** - Docker支持
3. **改善文档质量** - 最佳实践和示例
4. **提升用户体验** - 一键安装链接
5. **支持多种场景** - 个人、开发、企业

项目现在更加**易用**、**专业**、**完整**！ 🎉
