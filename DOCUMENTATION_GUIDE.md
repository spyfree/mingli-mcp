# 📚 Documentation Organization

## 目录结构

\`\`\`
ziwei_mcp/
├── README.md                          # 项目主文档（必读）
├── QUICKSTART.md                      # 快速开始指南
├── ARCHITECTURE.md                    # 系统架构设计
│
├── docs/
│   ├── README.md                      # 文档索引
│   └── development/                   # 开发文档（不提交到git）
│       ├── CHECK_RESULTS.md
│       ├── DIAGNOSIS.md
│       └── ...
│
├── 部署相关/
│   ├── DEPLOYMENT.md                  # 通用部署指南
│   ├── DEPLOYMENT_SUMMARY.md          # 部署方案对比
│   ├── CLOUDFLARE_DEPLOY.md           # Cloudflare部署
│   ├── CLOUDFLARE_EXPLAINED.md        # Cloudflare详解
│   ├── PYPI_PUBLISH.md                # PyPI发布指南
│   └── QUICK_START_PYPI.md            # PyPI快速开始
│
├── 客户端集成/
│   ├── MCP_CLIENT_CONFIG.md           # MCP客户端通用配置
│   ├── COZE_GUIDE.md                  # Coze集成指南
│   ├── COZE_CONFIG_GUIDE.md           # Coze详细配置
│   └── CURSOR_SETUP.md                # Cursor设置
│
└── 实现细节/
    ├── BAZI_IMPLEMENTATION.md         # 八字系统实现
    └── PROJECT_SUMMARY.md             # 项目总结
\`\`\`

---

## 文档分类

### 🎯 用户文档（提交到GitHub）

这些文档面向最终用户，包含在仓库中：

#### 入门指南
- **README.md** - 项目概览、功能介绍、快速开始
- **QUICKSTART.md** - 详细的快速入门教程
- **QUICK_START_PYPI.md** - PyPI安装快速指南

#### 架构与实现
- **ARCHITECTURE.md** - 系统架构设计文档
- **BAZI_IMPLEMENTATION.md** - 八字系统实现详解
- **PROJECT_SUMMARY.md** - 项目总结和特性说明

#### 部署指南
- **DEPLOYMENT.md** - 通用部署指南（包括各种云平台）
- **DEPLOYMENT_SUMMARY.md** - 部署方案对比和推荐
- **CLOUDFLARE_DEPLOY.md** - Cloudflare Tunnel详细配置
- **CLOUDFLARE_EXPLAINED.md** - Cloudflare vs 其他方案详解
- **PYPI_PUBLISH.md** - PyPI完整发布流程

#### 客户端集成
- **MCP_CLIENT_CONFIG.md** - 通用MCP客户端配置
- **COZE_GUIDE.md** - Coze平台集成指南
- **COZE_CONFIG_GUIDE.md** - Coze详细配置说明
- **CURSOR_SETUP.md** - Cursor IDE设置

---

### 🔧 开发文档（本地保留）

这些文档是开发调试过程记录，**不提交到git**，存放在 \`docs/development/\`：

#### 调试记录
- **DIAGNOSIS.md** - 问题诊断过程
- **CHECK_RESULTS.md** - 检查结果报告
- **DEPLOYMENT_CHECK.md** - 部署检查清单

#### 修复过程
- **PYPI_FIXED.md** - PyPI问题修复过程
- **SUCCESS_REPORT.md** - 部署成功报告
- **QUICK_FIX_CODEX.md** - Codex快速修复

#### 配置示例
- **CODEX_CONFIG.md** - Codex配置详解
- **CODEX_TROUBLESHOOTING.md** - Codex问题排查
- **CLOUDFLARE_TUNNEL_SETUP.md** - Cloudflare设置步骤

#### 升级指南
- **UPGRADE_GUIDE.md** - 版本升级指南
- **UPLOAD_TO_PYPI.md** - PyPI上传步骤

---

## 为什么这样组织？

### ✅ 优点

1. **保持仓库整洁**
   - GitHub只显示必要的用户文档
   - 减少信息过载
   - 提升专业度

2. **保留开发记录**
   - 本地保留所有调试过程
   - 便于未来参考
   - 不影响远程仓库

3. **清晰的文档分类**
   - 用户容易找到需要的文档
   - 开发者有完整的调试记录
   - 维护者清楚文档用途

### 📋 .gitignore规则

\`\`\`gitignore
# Development documentation (internal debugging notes)
docs/development/

# Configuration examples (local only)
codex_config_correct.toml
\`\`\`

---

## 如何添加新文档？

### 用户文档（需要提交）

\`\`\`bash
# 直接在根目录创建
touch NEW_FEATURE.md

# 编辑并提交
git add NEW_FEATURE.md
git commit -m "Add documentation for new feature"
git push
\`\`\`

### 开发文档（本地保留）

\`\`\`bash
# 在development目录创建
touch docs/development/DEBUG_NOTES.md

# 编辑保存，不需要提交
# .gitignore会自动忽略
\`\`\`

---

## 文档更新流程

### 更新现有文档

\`\`\`bash
# 编辑文档
nano README.md

# 查看变更
git diff README.md

# 提交
git add README.md
git commit -m "Update README: add new installation method"
git push
\`\`\`

### 清理旧文档

\`\`\`bash
# 移动到development目录
mv OLD_DOC.md docs/development/

# 如果已经在git中，需要删除追踪
git rm --cached OLD_DOC.md
git commit -m "Move OLD_DOC.md to development folder"
git push
\`\`\`

---

## 文档最佳实践

### ✅ 用户文档应该

- 清晰明了，面向非技术用户
- 包含完整的步骤和示例
- 保持更新，与代码同步
- 使用标准Markdown格式
- 添加适当的emoji增加可读性

### ✅ 开发文档应该

- 详细记录问题和解决过程
- 包含错误信息和调试步骤
- 记录时间戳和版本信息
- 可以更随意，重点是完整性

### ❌ 避免

- 在用户文档中包含调试细节
- 在GitHub暴露敏感信息
- 重复的文档内容
- 过时的配置示例

---

## 文档索引

完整的文档索引请查看：
- **[docs/README.md](docs/README.md)** - 所有文档的分类索引

---

## 快速查找

**想要...**

- 快速开始？ → [QUICKSTART.md](QUICKSTART.md)
- 部署到云端？ → [DEPLOYMENT.md](DEPLOYMENT.md)
- 发布到PyPI？ → [PYPI_PUBLISH.md](PYPI_PUBLISH.md)
- 集成到Coze？ → [COZE_GUIDE.md](COZE_GUIDE.md)
- 配置Cursor？ → [CURSOR_SETUP.md](CURSOR_SETUP.md)
- 了解架构？ → [ARCHITECTURE.md](ARCHITECTURE.md)

---

**📌 提示**：所有在 \`docs/development/\` 目录下的文件不会被提交到GitHub，但会保留在你的本地仓库中供参考。
