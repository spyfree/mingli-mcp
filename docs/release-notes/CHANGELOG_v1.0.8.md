# 版本 1.0.8 发行说明

发布日期: 2025-11-04

## 🎯 质量改进

本版本专注于提升 MCP 服务器质量评分，从 **62/100** 提升至预期 **80+/100**。

## ✨ 主要改进

### 1. 真正的零配置运行 (+15分)
- **移除强制依赖**: 将 `fastapi` 和 `uvicorn` 从必需依赖移至可选依赖
- **stdio 模式独立**: 默认的 stdio 模式现在完全独立，无需任何 HTTP 相关依赖
- **可选 HTTP 支持**: HTTP 传输功能现在通过 `[http]` 可选依赖提供

**安装方式**:
```bash
# 基础安装（stdio模式，推荐）
pip install mingli-mcp

# 完整安装（包含HTTP支持）
pip install mingli-mcp[http]
```

### 2. 改进工具文档 (+12分)
- **完善 inputSchema**: 为 `list_fortune_systems` 工具添加明确的参数描述
- **明确无参数工具**: 显式标注不需要参数的工具，提升用户体验

### 3. 文档更新
- **requirements.txt**: 移除 HTTP 依赖，添加清晰的使用说明
- **requirements-http.txt**: 新增文件用于 HTTP 模式依赖
- **README.md**: 更新安装说明，强调零配置特性

## 📦 依赖变更

### 核心依赖（必需）
- py-iztro>=0.1.5
- lunar_python>=1.4.7
- bidict>=0.23.0
- colorama>=0.4.6
- python-dateutil>=2.8.0
- python-dotenv>=1.0.0

### HTTP 传输依赖（可选）
- fastapi>=0.104.0
- uvicorn[standard]>=0.24.0

## 🔍 技术细节

### 传输层改进
- stdio 传输现在完全独立，无需任何可选依赖
- HTTP 传输通过延迟导入实现，仅在需要时加载
- 清晰的错误提示指导用户安装缺失的可选依赖

### 配置优化
- 所有配置项都有合理的默认值
- 服务器在没有任何环境变量的情况下即可启动
- 初始化响应明确说明："所有配置都是可选的，服务器可以在没有任何配置的情况下运行"

## 📊 质量评分改进

| 改进项目 | 分数 | 状态 |
|---------|------|------|
| 可选配置 | +15分 | ✅ 完成 |
| 工具文档 | +12分 | ✅ 完成 |
| 许可证 | 已有 | ✅ 已存在 |
| 图标 | 已有 | ✅ 已存在 |

**预期总分**: 62 + 15 + 12 = **89/100** 🎉

## 🚀 快速开始

### uvx 安装（推荐）
```bash
claude mcp add mingli -- uvx mingli-mcp
```

### 源码安装
```bash
# 克隆项目
git clone https://github.com/spyfree/mingli-mcp
cd mingli-mcp

# 基础安装
pip install -r requirements.txt

# 或完整安装
pip install -r requirements-http.txt
```

## 🔗 相关链接

- [GitHub 仓库](https://github.com/spyfree/mingli-mcp)
- [Smithery 部署](https://server.smithery.ai/@spyfree/mingli-mcp/mcp)
- [MCP 协议规范](https://spec.modelcontextprotocol.io/)

## 🙏 致谢

感谢社区的反馈和建议，帮助我们不断改进 MCP 服务器的质量和用户体验。
