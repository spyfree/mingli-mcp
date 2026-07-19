# 更新日志

## [1.1.0] - 2026-07-19

### 重大变更 ⚠️

- **包结构重构**: 所有代码收进单一 `mingli_mcp` 包命名空间。此前 wheel 会向 site-packages 安装顶层的 `mcp`、`core`、`utils`、`systems`、`transports`、`config`，与官方 MCP Python SDK（PyPI `mcp` 包）及其他包冲突；现在 wheel 只含 `mingli_mcp/`，已验证可与官方 `mcp` SDK 共存安装
- **入口变更**: 源码运行方式从 `python mingli_mcp.py` 改为 `python -m mingli_mcp`；`mingli-mcp` 控制台脚本和 uvx 用法不变

### MCP 协议合规（对齐 2025-11-25 规范）

- **协议版本协商**: `initialize` 按客户端请求的 `protocolVersion` 协商（支持 2024-11-05 ~ 2025-11-25），不再硬编码 2024-11-05
- **resources/read**: 支持标准方法名（原实现只支持非标准的 `resources/get`，标准客户端无法读取资源）；响应补全 `uri`、`mimeType` 字段；保留 `resources/get` 兼容
- **notification 语义**: 对无 `id` 的消息（notification）不再发送任何响应；HTTP 端点按规范返回 202 Accepted 无 body（此前返回带 body 的 204，违反 HTTP 规范）
- **Origin 校验**: HTTP 端点校验 `Origin` 头，非法来源返回 403（规范强制要求，防 DNS rebinding）
- **MCP-Protocol-Version 头校验**: 不支持的版本返回 400
- **ping**: 支持 `ping` 方法；`resources/templates/list` 返回空列表而非 Method not found

### Bug 修复

- **真太阳时参数生效**: `longitude`/`latitude`/`use_solar_time`/`birth_hour`/`birth_minute` 此前在 MCP handler 中被静默丢弃，修正后真正传入排盘系统；并补充到 `get_ziwei_fortune`、`analyze_ziwei_palace` 的参数 schema
- **stdio 健壮性**: 一行坏 JSON 不再导致服务器退出，改为返回 -32700 Parse error 并继续处理
- **限流真实生效**: Cloudflare 部署下按 `CF-Connecting-IP`/`X-Forwarded-For` 分桶（此前所有外部用户共享代理 IP 的一个桶）；`ENABLE_RATE_LIMIT`/`RATE_LIMIT_*` 环境变量真正被读取；`RateLimiter` 线程安全
- **事件循环不再被阻塞**: 排盘计算移入线程池执行，长计算期间 `/health` 保持可用
- **prompts 随包发布**: prompts 目录移入包内，pip/uvx 安装后 `prompts/list` 不再为空
- **query_date 校验**: 非法日期返回 -32602 参数错误而非 -32603 内部错误
- **版本号统一**: 包版本单一来源（`mingli_mcp.__version__`），HTTP 根路径不再显示过期的 1.0.0
- **docker-compose 健康检查**: 改用 python 探活（slim 镜像无 curl）
- **系统注册失败可见**: `systems` 注册的 ImportError 记录 warning 而非静默吞掉

### 依赖

- `iztro-py` 升级到 `>=0.4.0`

## [1.0.16] - 2026-03-07

### Bug 修复

- **对齐 iztro-py 0.3.4**: 将依赖下限升级到 `iztro-py>=0.3.4`，确保紫微排盘与最新核心库保持一致
- **修复运势翻译泄漏内部 ID**: `get_ziwei_fortune` 现在会把 `palace_names` 和 `mutagen` 从 `surfacePalace` / `tanlangMaj` 这类内部值翻译为用户可读名称
- **修复流时边界时辰映射**: 运势查询现在按 iztro-py 的早/晚子时规则处理 `23:xx` 和 `00:xx`
- **恢复旧宫位别名兼容**: `analyze_ziwei_palace` 继续接受 `财帛`、`官禄`、`仆役/奴仆` 等旧输入，并统一映射到最新宫位名称

## [1.0.13] - 2025-01-07

### 重大变更 ⚠️

**宫位名称统一化**（破坏性变更）

为了与 iztro-py 库保持一致，所有宫位名称（除"命宫"外）现在都带"宫"字：

- **之前**: `["命宫", "兄弟", "夫妻", "子女", "财帛", "疾厄", "迁移", "仆役", "官禄", "田宅", "福德", "父母"]`
- **现在**: `["命宫", "兄弟宫", "夫妻宫", "子女宫", "财帛宫", "疾厄宫", "迁移宫", "交友宫", "官禄宫", "田宅宫", "福德宫", "父母宫"]`

**迁移指南**:

```python
# 之前
result = ziwei.analyze_palace(birth_info, "父母")

# 现在
result = ziwei.analyze_palace(birth_info, "父母宫")
```

"命宫"保持不变，无需修改。

### Bug 修复

- **修复宫位查询错误**: 解决 `analyze_ziwei_palace` 工具无法查询非命宫的宫位的问题
  - 原因：PALACES 常量定义的名称（不带"宫"）与 formatter 输出的名称（带"宫"）不一致
  - 影响：Smithery playground 上所有宫位查询（除命宫外）都会失败
  - 修复：统一所有宫位名称格式，与 iztro-py 输出保持一致

- **统一宫位命名**: 将"仆役宫"改为"交友宫"，与 iztro-py 的 friendsPalace 保持一致

### 改进

- **排盘准确性提升**: 受益于 iztro-py 0.3.2 的算法修复
  - 修复父母宫主星判断错误（1989-10-17 午时案例）
  - 修复命宫、身宫地支定位问题
  - 提升整体排盘准确性

- **依赖更新**: 确保使用 iztro-py >= 0.3.1，受益于上游库的持续改进

### 文档

- 添加 `PALACE_NAME_FIX.md`：详细的问题分析和修复说明

---

## [1.0.12] - 2025-01-07

### Bug 修复

- **修复星曜名称拼写错误**: 升级到 iztro-py 0.3.1，修复上游库的星曜名称拼写错误

### 依赖更新

- 升级 iztro-py: 0.3.0 → 0.3.1

---

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
