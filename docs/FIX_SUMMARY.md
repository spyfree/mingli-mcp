# mingli-mcp 连接问题修复说明

## 问题

使用 `claude mcp add mingli -- uvx mingli-mcp` 时出现连接失败：
```
ModuleNotFoundError: No module named 'uvicorn'
```

## 修复内容

### 1. 修改 `transports/__init__.py`
- 将 HTTP 传输改为可选导入（延迟导入）
- 添加 `HTTP_TRANSPORT_AVAILABLE` 标志
- 当缺少依赖时，HTTP 传输为 `None`

### 2. 修改 `mingli_mcp.py`
- 在初始化传输层时检查 `HTTP_TRANSPORT_AVAILABLE`
- 当 HTTP 不可用时提供清晰的错误信息
- 允许 stdio 模式独立运行，无需 uvicorn

### 3. 重新构建包
- 构建了 mingli-mcp 1.0.5 版本
- 包含所有修复

## 测试结果

✅ 系统安装版本：正常启动
✅ 包结构：所有模块可导入
✅ 传输层：stdio 模式无需 HTTP 依赖

## 使用方法

### 方案一：系统安装（推荐）
```bash
pip install mingli-mcp
```

### 方案二：uvx 运行
```bash
uvx mingli-mcp
```

## 配置文件

在 Claude Desktop 中配置：

```yaml
mcpServers:
  mingli:
    command: "mingli-mcp"
    args: []
    env: {}
```

## 文档

详细说明请参考：`TROUBLESHOOTING.md`

## 版本信息

- **版本**：mingli-mcp 1.0.5
- **修复日期**：2025-10-28
- **修复类型**：依赖解耦，传输层优化