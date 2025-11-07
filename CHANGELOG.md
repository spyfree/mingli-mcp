# 更新日志

## [1.0.11] - 2025-11-07

### 改进
- **Smithery质量分数提升**: 移除initialize响应中的configSchema，实现真正的零配置体验
  - 所有配置通过环境变量和合理默认值处理
  - 用户无需任何配置即可直接运行服务器
  - 预期获得 +15 分的 "Optional configuration" 评分

### 技术细节
- 保留smithery.yaml中的空configSchema（针对Smithery部署）
- 服务器initialize响应中不再返回configSchema字段
- 通过instructions字段说明可用的环境变量配置选项

---

## [1.0.10] - 2025-11-07

### 新功能
- **多语言支持**: 添加i18n国际化支持
  - 支持简体中文(zh-CN)、繁体中文(zh-TW)、英语(en-US)
  - 支持日语(ja-JP)、韩语(ko-KR)、越南语(vi-VN)
  - 通过 `DEFAULT_LANGUAGE` 环境变量配置默认语言
  - 工具调用时可通过 `language` 参数指定输出语言

### 改进
- 升级到 iztro-py 0.3.0，使用原生i18n翻译方法
- 优化formatter，支持多语言星曜名称和宫位名称翻译

---

## [1.0.9] - 2025-11-07

### 重大变更
- **性能提升**: 从 py-iztro 迁移到 iztro-py
  - 10倍性能提升（从100ms降至10ms）
  - 更好的类型安全和代码质量
  - 完整的英文文档和IDE支持
  - 详见 `MIGRATION_EVALUATION.md` 的完整评估报告

### 新增
- 添加性能对比测试脚本 `benchmark_iztro_comparison.py`
- 添加API兼容性分析脚本 `api_compatibility_analysis.py`
- 完整的迁移评估文档

### 代码质量
- 修复所有flake8 linting错误
- 统一代码格式化（black）
- 优化import顺序（isort）

---

## [1.0.8] - 2025-11-04

### 质量改进
- **零配置运行**: 将 fastapi 和 uvicorn 移至可选依赖
- **改进工具文档**: 完善 inputSchema 描述
- **预期质量评分**: 从 62/100 提升至 89/100

详见: `CHANGELOG_v1.0.8.md`

---

## [1.0.7] 及更早版本

### 核心功能
- 紫微斗数系统 (Ziwei Doushu)
- 八字系统 (BaZi/Four Pillars)
- MCP协议支持
- stdio和HTTP传输方式
- 提示词(Prompts)和资源(Resources)支持
- Docker和uvx部署支持
