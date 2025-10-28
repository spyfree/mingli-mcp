# mingli-mcp 连接问题解决指南

## 问题描述

使用 `claude mcp add mingli -- uvx mingli-mcp` 添加 MCP 服务时，出现以下错误：

```
Failed to reconnect to mingli.
ModuleNotFoundError: No module named 'uvicorn'
```

## 根本原因

1. **依赖问题**：`uvicorn` 是 HTTP 传输的必需依赖，但同时也是所有模式的依赖
2. **可选依赖**：当使用 `uvx` 运行 mingli-mcp 时，依赖没有正确安装
3. **传输层设计**：HTTP 和 stdio 传输耦合过紧，stdio 模式不需要 HTTP 相关依赖

## 解决方案

### 方案一：使用系统安装版本（推荐）

**优点**：稳定、快速、不需要每次下载依赖

```bash
# 1. 安装 mingli-mcp 到系统
pip install mingli-mcp

# 2. 在 Claude Desktop 中配置
claude mcp add mingli /path/to/mingli-mcp
```

### 方案二：使用 uvx 并配置正确（需要首次构建）

**优点**：使用最新版本、自动处理依赖

#### 步骤 1：清理 uv 缓存
```bash
uv cache clean
```

#### 步骤 2：重新构建包
```bash
cd /path/to/mingli-mcp
python -m build
```

#### 步骤 3：安装到系统
```bash
uv pip install --system dist/mingli_mcp-1.0.5-py3-none-any.whl
```

#### 步骤 4：测试连接
```bash
# 简单测试
mingli-mcp

# 或使用 uvx（首次可能需要下载依赖）
uvx mingli-mcp
```

### 方案三：手动指定本地包路径

如果你有本地构建的包：

```bash
claude mcp add mingli -- python /path/to/mingli_mcp.py
```

## 配置文件示例

### Claude Desktop 配置

**使用系统安装版本** (`~/.config/claude/claude_desktop_config.yaml`):

```yaml
mcpServers:
  mingli:
    command: "mingli-mcp"
    args: []
    env: {}
```

**使用 uvx 版本** (`~/.config/claude/claude_desktop_config.yaml`):

```yaml
mcpServers:
  mingli:
    command: "uvx"
    args: ["mingli-mcp"]
    env: {}
```

**使用本地路径** (`~/.config/claude/claude_desktop_config.yaml`):

```yaml
mcpServers:
  mingli:
    command: "python"
    args: ["/path/to/mingli-mcp/mingli_mcp.py"]
    env:
      TRANSPORT_TYPE: "stdio"
```

## 验证安装

运行以下命令验证安装：

```python
#!/usr/bin/env python3
import subprocess
import sys

# 测试系统安装版本
try:
    process = subprocess.Popen(
        ["mingli-mcp"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    import time
    time.sleep(1)

    if process.poll() is None:
        print("✅ mingli-mcp 安装成功")
        process.terminate()
        process.wait(timeout=2)
        sys.exit(0)
    else:
        print("❌ mingli-mcp 启动失败")
        sys.exit(1)

except Exception as e:
    print(f"❌ 测试失败: {e}")
    sys.exit(1)
```

## 已知问题

### Q: 使用 uvx 时仍然提示缺少依赖

**A**: 这是因为 uvx 使用缓存的虚拟环境。解决：
1. 清理缓存：`uv cache clean`
2. 等待依赖下载完成（首次运行可能需要几分钟）
3. 或者使用系统安装版本

### Q: HTTP 传输模式不可用

**A**: HTTP 传输需要 uvicorn 依赖。解决方案：

```bash
# 完整安装（包含所有依赖）
pip install mingli-mcp[http]

# 或安装完整依赖
pip install mingli-mcp
```

### Q: 如何切换传输模式

**A**: 通过环境变量配置：

```bash
# stdio 模式（默认，用于 MCP）
export TRANSPORT_TYPE=stdio
mingli-mcp

# HTTP 模式（用于 Web 服务）
export TRANSPORT_TYPE=http
export HTTP_HOST=0.0.0.0
export HTTP_PORT=8080
mingli-mcp
```

## 版本信息

- **当前版本**：mingli-mcp 1.0.5
- **修复内容**：
  - HTTP 传输改为可选导入
  - stdio 模式不再强制依赖 uvicorn
  - 提供更清晰的错误信息

## 技术细节

### 依赖关系图

```
mingli-mcp
├── 核心依赖（所有模式必需）
│   ├── py-iztro
│   ├── lunar_python
│   ├── bidict
│   ├── colorama
│   ├── python-dateutil
│   ├── python-dotenv
│   └── fastapi
└── HTTP 传输依赖（仅 HTTP 模式需要）
    └── uvicorn[standard]
```

### 传输层架构

```
MingliMCPServer
├── StdioTransport（默认，MCP 标准）
│   └── 不依赖 uvicorn
└── HttpTransport（可选，Web 服务）
    └── 需要 uvicorn
```

## 总结

最佳实践是**使用系统安装版本**，这样可以避免依赖问题，提供最佳性能和稳定性。

```bash
# 最简单的解决方案
pip install mingli-mcp
claude mcp add mingli /path/to/mingli-mcp
```