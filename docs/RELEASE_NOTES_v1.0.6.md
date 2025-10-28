# 发行说明 - mingli-mcp v1.0.6

## 发行信息

- **版本**：v1.0.6
- **发行日期**：2025-10-28
- **状态**：✅ 已发布

## 🔧 重要修复

### 问题修复

- **修复 mingli-mcp 连接失败问题**
  - 解决使用 `uvx mingli-mcp` 时出现 `ModuleNotFoundError: No module named 'uvicorn'` 错误
  - 将 HTTP 传输依赖从强耦合改为可选导入
  - stdio 模式现在可以独立运行，无需 uvicorn 依赖

### 技术改进

1. **传输层解耦**
   - 修改 `transports/__init__.py`：HTTP 传输改为可选导入
   - 添加 `HTTP_TRANSPORT_AVAILABLE` 标志用于运行时检测
   - 当 HTTP 不可用时提供清晰的错误信息

2. **错误处理优化**
   - 修改 `mingli_mcp.py`：添加依赖检查逻辑
   - 提供详细的安装建议和错误提示
   - 改善用户体验

3. **版本更新**
   - 升级至 v1.0.6
   - 更新配置文件版本号

## 📚 新增文档

### 故障排除指南

- **TROUBLESHOOTING.md**：完整的故障排除指南
  - 详细的问题描述和解决方案
  - 三种使用方案对比
  - 常见问题解答
  - 配置文件示例

### 修复说明

- **FIX_SUMMARY.md**：技术修复说明
  - 问题根本原因分析
  - 修复内容详情
  - 验证结果

### 使用指南

- **UVX_SETUP_GUIDE.md**：uvx 使用指南
  - 如何使用 uvx 运行 mingli-mcp
  - 配置说明
  - 最佳实践

### 配置示例

- **examples/config/uvx_mcp_config_correct.json**：正确配置示例
  - Claude Desktop 配置示例
  - 各种运行方式配置

## 🚀 使用方法

### 方案一：系统安装（推荐）

```bash
# 安装
pip install mingli-mcp

# 使用
claude mcp add mingli /path/to/mingli-mcp
```

### 方案二：uvx 运行

```bash
# 清理缓存（首次使用）
uv cache clean

# 使用
claude mcp add mingli -- uvx mingli-mcp
```

### 方案三：本地路径

```bash
claude mcp add mingli -- python /path/to/mingli-mcp/mingli_mcp.py
```

## 🏗️ 构建产物

已发布到 PyPI：

- **mingli-mcp-1.0.6-py3-none-any.whl** (117 KB)
- **mingli-mcp-1.0.6.tar.gz** (118 KB)

## ✅ 验证结果

- ✅ 系统安装版本正常启动
- ✅ 包结构完整，所有模块可导入
- ✅ stdio 模式无需 HTTP 依赖
- ✅ 版本信息正确：v1.0.6
- ✅ 成功发布到 PyPI
- ✅ 可以正常从 PyPI 安装使用

## 📦 PyPI 信息

- **包名**：mingli-mcp
- **版本**：1.0.6
- **PyPI 链接**：https://pypi.org/project/mingli-mcp/1.0.6/
- **安装命令**：`pip install mingli-mcp`

## 🔗 相关链接

- **GitHub 仓库**：https://github.com/spyfree/mingli-mcp
- **PyPI 页面**：https://pypi.org/project/mingli-mcp/
- **文档目录**：docs/
  - TROUBLESHOOTING.md - 故障排除指南
  - FIX_SUMMARY.md - 修复说明
  - UVX_SETUP_GUIDE.md - uvx 使用指南

## 🙏 致谢

感谢所有用户的反馈，帮助我们发现并修复了这个重要问题！

---

**快速开始**：

```bash
pip install mingli-mcp
```

**配置 Claude Desktop**：

编辑 `~/.config/claude/claude_desktop_config.yaml`：

```yaml
mcpServers:
  mingli:
    command: "mingli-mcp"
    args: []
    env: {}
```