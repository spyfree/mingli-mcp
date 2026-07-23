# 更新日志

## [1.2.0] - 2026-07-25

### 重大变更 ⚠️

- **八字四柱换柱边界修正**: 四柱改用 lunar_python 的 `EightChar` 接口。此前用
  `Lunar.getYearInGanZhi()`（按农历新年换年）和 `Lunar.getMonthInGanZhi()`，
  而八字要求年柱按**立春**换、月柱按**节**的精确时刻换。随机 4000 例抽样中
  年柱错误率 2.10%、月柱错误率 1.75%（合计约 3.8% 的命盘至少有一柱不同）。
  生肖同步改为立春口径，避免与年柱自相矛盾。**受影响命盘的排盘结果会与旧版本不同，
  新结果才是正确的。**

### OAuth 与客户端体验

- **标准 OAuth 2.1 接入**: Cloudflare MCP 网关新增授权服务器元数据、受保护资源元数据、动态客户端注册、S256 PKCE 授权码交换和刷新令牌，主流客户端可自动发现并发起连接
- **License 授权页**: 新增移动端友好的授权确认页；用户只需在授权时输入已购买的 MCP License Key，Key 不进入 URL，也不以明文写入 OAuth 可读元数据
- **向后兼容**: 保留 `Authorization: Bearer ML-...` 和内部主密钥；`initialize`、`tools/list` 等发现方法继续免费开放，`tools/call` 对 OAuth 与旧 Key 统一执行每日额度
- **客户端可理解性**: 工具补齐标题、只读/幂等/封闭世界提示和严格输入 schema；初始化说明改为面向 AI 助手的采集与展示规则，明确区分本命生肖和流年生肖
- **自动化验证**: 新增 Worker 级黑盒测试，覆盖 OAuth discovery、CSRF、PKCE、旧 Key、额度与容器转发

### 新功能

- **八字大运完整推演**: `get_bazi_fortune` 不再是"年龄除以10"的占位实现。现在输出
  起运时间（由出生到月令节气的距离换算）、顺逆排方向（阳男阴女顺排 / 阴男阳女逆排）、
  十步大运干支及各步十神与旬空、起运前小运期标记、当前所处大运、流年干支与十神。
  已用 600 个随机命例交叉验证顺逆排规则、干支六十甲子推移和年龄年份连续性。
- **地支藏干十神**: `get_bazi_chart` 新增 `zhi_deities` 字段（此前代码注释为"简化处理"，
  未实现），与 lunar_python 的十神实现交叉验证一致。

### Bug 修复

- **stdio 会话不再被畸形消息终结**: 合法 JSON 但非对象的消息（`[]`、`123`、`"x"`、
  `null`）会在 `handle_request` 抛 AttributeError，异常逃出 stdio 消息循环导致整个会话
  结束，后续请求全部无响应、客户端挂死。现返回 -32600，且单条消息处理失败不再终结循环
- **八字农历闰月被忽略**: `is_leap_month` 未传给 lunar_python（闰月需用负月份表示），
  闰月生辰会静默返回非闰月的盘；紫微本来是正确处理的，两个系统结果互相矛盾
- **八字农历输入时 `solar_date` 错误**: 直接回显了农历日期，现正确换算为阳历
- **晚子时真太阳时修正落在错误时辰**: 时辰 12（23:00-24:00）与早子时共用 00:00 中点
- **八字运势接受早于出生的查询日期**: 曾输出 `age=-10`、`第0个大运`、`-10--1岁`
- **西经显示为东经**: `format_solar_time_info` 把 -74.0 显示成 `-74.0°E`
- **紫微 Markdown 宫位标题重复"宫"字**: 宫位名本身已含"宫"，默认输出渲染为"命宫宫"

### 参数校验

- `time_index` 为非整数时抛 TypeError（表现为 -32603 内部错误），现返回 -32602 参数错误
- `calendar` 从不校验，非法值被静默当作阳历处理
- `longitude`/`latitude`/`birth_hour`/`birth_minute` 在 inputSchema 声明了 min/max 但服务端不校验
- `use_solar_time` 缺 `longitude` 时静默跳过修正，现明确报错

### 协议合规

- JSON-RPC 响应此前在 id 未知时省略 `id` 字段，规范要求该字段必须存在（未知时为 null）

### 安全

- **限流可被绕过**: 无条件信任客户端可控的 `CF-Connecting-IP`/`X-Forwarded-For`，
  轮换请求头即可让每个请求算作新客户端。现由 `TRUST_PROXY_HEADERS` 控制（默认 false），
  仅在可信代理后开启
- **`/stats` 未授权访问**: 未配置 `HTTP_API_KEY` 时该端点对所有人开放限流器内部状态，现返回 404

### 可观测性

- **工具调用指标接入**: `utils/metrics.py` 有198行实现却从未被服务器调用过。现在每次
  `tools/call` 都会记录系统、方法、耗时、成败与错误类型，并通过 `/stats` 暴露
  （需配置 `HTTP_API_KEY`）。`/stats` 返回结构改为 `{tool_calls, rate_limiting}`
- 删除 `utils/performance.py` 中与之重复且同样未接入的 `PerformanceMetrics`/`global_metrics`
  （仍在使用的 `PerformanceTimer` 与 `log_performance` 保留）

### 工程整理

- **修复 `npm ci` 在镜像源之外无法安装**: `package-lock.json` 里 90 个 `resolved`
  URL 全部硬编码为 `registry.npmmirror.com`。`npm ci` 会照这些 URL 取包，因此在无法
  访问该镜像的环境（海外网络、CI runner、沙箱）会直接 403 失败，Cloudflare 部署前的
  `npm ci` 因此走不通。已按 `registry.npmjs.org` 重新生成 lockfile（版本仍在
  package.json 声明范围内：wrangler 4.114.0、@cloudflare/containers 0.1.1）

- **mypy 成为真正的 CI 门禁**: 此前 CI 里是 `mypy . || true`，26 个错误从不会让 CI 变红。
  现已清零并去掉 `|| true`；仅对 4 个直接跨越无类型第三方边界的模块局部关闭
  `warn_return_any`（逐个 cast 只增噪音不提升正确性），并在 pyproject 中注明原因
- **删除失效脚本 `test_security_fixes.py`**: 它读取 1.1.0 重构时已删除的 `mingli_mcp.py`，
  实际运行结果是 0/4 通过；且位于 `testpaths` 之外，CI 从未执行
- **根目录整理**: 17 个 markdown 精简到 5 个（README/CHANGELOG/CLAUDE/AGENTS/DEV_COMMANDS），
  历史发布说明移入 `docs/release-notes/`，改进记录移入 `docs/development/`；
  `api_compatibility_analysis.py`、`benchmark_iztro_comparison.py` 移入 `scripts/`
- **紫微四柱口径说明**: 紫微以农历年换年干支、八字以立春换年，立春前后两者年柱/月柱会不同。
  这是流派差异而非错误，已在 `get_ziwei_chart` 的工具描述和 Markdown 输出中明确标注
  （紫微安星本身依赖农历年，未改动其计算）

### 其他

- 新增 `[http]` extra：`pip install mingli-mcp[http]` 此前被服务端报错信息、README、
  docs 引用但并不存在
- `analyze_element` 纳入 `BaseFortuneSystem` 接口；`BaziFormatter` 补充返回 str 的
  Markdown 方法；mypy 错误从 26 降至 8（剩余均为无类型第三方库边界）
- 四处版本号对齐到本次发布：`server.json`（停留在 1.0.7）、`package.json`（停留在 1.0.10）、`.actor/actor.json`（停留在 1.1，Apify 用 MAJOR.MINOR），此前均与包版本不一致
- 新增 75 个回归测试，覆盖率 82% → 85%

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
