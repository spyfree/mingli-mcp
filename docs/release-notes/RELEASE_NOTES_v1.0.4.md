# Release Notes v1.0.4

**发布日期**: 2025-10-28

## 🎉 主要更新

### ✅ Smithery 部署成功
- 修复了 Docker 构建问题（pythonmonkey 依赖需要 Node.js）
- 成功部署到 Smithery 平台
- 在线服务地址: https://server.smithery.ai/@spyfree/mingli-mcp/mcp

### 📦 发布渠道

1. **PyPI**: https://pypi.org/project/mingli-mcp/1.0.4/
   - 可通过 `uvx mingli-mcp` 或 `pip install mingli-mcp` 安装

2. **GitHub**: https://github.com/spyfree/mingli-mcp
   - Tag: v1.0.4
   - 完整源码和文档

3. **Smithery**: https://server.smithery.ai/@spyfree/mingli-mcp/mcp
   - 在线 MCP 服务
   - 无需本地安装，直接使用

## 🔧 技术改进

### Docker 构建优化
- 添加 Node.js 20.x 安装步骤
- 解决 pythonmonkey 构建依赖问题
- 优化镜像构建流程

### 文档更新
- README 新增 Smithery 部署链接
- 完善部署方式说明
- 添加在线体验入口

## 📝 变更日志

### Commits
```
a692afc Release v1.0.4: Add Smithery deployment and fix Docker build
2398512 Fix: Add Node.js installation to Dockerfile for pythonmonkey dependency
639446b Fix: Correct smithery.yaml format for Smithery deployment
```

### 文件变更
- `Dockerfile`: 添加 Node.js 安装步骤
- `README.md`: 添加 Smithery 部署链接
- `pyproject.toml`: 版本升级至 1.0.4

## 🚀 使用方式

### 方式1: uvx (最简单)
```bash
uvx mingli-mcp
```

### 方式2: Smithery (在线)
直接访问: https://server.smithery.ai/@spyfree/mingli-mcp/mcp

### 方式3: Docker
```bash
docker-compose up -d
```

### 方式4: pip 安装
```bash
pip install mingli-mcp==1.0.4
```

## 📊 项目统计

- **功能**: 紫微斗数 + 八字完整实现
- **MCP 工具**: 7个（紫微3个 + 八字3个 + 系统列表1个）
- **部署平台**: PyPI + GitHub + Smithery
- **Python 支持**: 3.8 - 3.13

## 🙏 致谢

感谢所有使用和反馈的用户！

---

**下载链接**:
- PyPI: https://pypi.org/project/mingli-mcp/1.0.4/
- GitHub: https://github.com/spyfree/mingli-mcp/releases/tag/v1.0.4
- Smithery: https://server.smithery.ai/@spyfree/mingli-mcp/mcp
