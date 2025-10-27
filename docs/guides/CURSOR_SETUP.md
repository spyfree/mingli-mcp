# Cursor MCP 配置完成

## ✅ 配置状态

**MCP服务器已成功添加到Cursor！**

### 配置信息
- **服务器名称**: `mingli`
- **配置文件**: `~/.cursor/mcp.json`
- **Python路径**: `/Users/lix18854/Documents/code/ziwei_mcp/venv/bin/python` ✅
- **脚本路径**: `/Users/lix18854/Documents/code/ziwei_mcp/mingli_mcp.py` ✅
- **JSON格式**: ✅ 验证通过

### 配置详情
```json
{
  "mingli": {
    "command": "/Users/lix18854/Documents/code/ziwei_mcp/venv/bin/python",
    "args": [
      "/Users/lix18854/Documents/code/ziwei_mcp/mingli_mcp.py"
    ],
    "env": {
      "LOG_LEVEL": "INFO",
      "DEFAULT_LANGUAGE": "zh-CN"
    }
  }
}
```

## 🚀 下一步操作

### 1. 重启Cursor
**必须重启Cursor才能加载新的MCP配置！**

```bash
# 方法1: 完全退出并重新打开Cursor
# macOS: Cmd+Q 完全退出，然后重新打开

# 方法2: 使用命令重启（如果Cursor支持）
# Cmd+Shift+P -> "Developer: Reload Window"
```

### 2. 验证MCP服务器
重启后，在Cursor中检查：

```bash
# 方法1: 使用MCP列表命令
# 在Cursor聊天中输入：
mcp list

# 应该能看到：
# - dataworks
# - chrome-devtools
# - mingli ✨ (新增)
```

### 3. 测试功能
在Cursor聊天中尝试：

```
帮我排一个紫微斗数盘：2000年8月16日，寅时，女性
```

或者：

```
查询1989年10月17日午时出生的男性，今天的紫微运势
```

或者：

```
列出所有可用的命理系统
```

## 🛠️ 可用工具

重启Cursor后，你将拥有以下4个新工具：

### 1. get_ziwei_chart
**功能**: 获取紫微斗数完整排盘
**参数**:
- date: 出生日期 (YYYY-MM-DD)
- time_index: 时辰序号 (0-12)
- gender: 性别 ("男"/"女")
- calendar: 历法 ("solar"/"lunar")，默认"solar"
- format: 输出格式 ("json"/"markdown")，默认"markdown"

### 2. get_ziwei_fortune
**功能**: 查询紫微斗数运势（大限、流年、流月、流日、流时）
**参数**:
- birth_date: 出生日期
- time_index: 时辰序号
- gender: 性别
- query_date: 查询日期（可选，默认今天）
- format: 输出格式

### 3. analyze_ziwei_palace
**功能**: 分析特定宫位详情
**参数**:
- birth_date: 出生日期
- time_index: 时辰序号
- gender: 性别
- palace_name: 宫位名称（命宫/兄弟/夫妻/子女/财帛/疾厄/迁移/仆役/官禄/田宅/福德/父母）
- format: 输出格式

### 4. list_fortune_systems
**功能**: 列出所有可用的命理系统及其功能

## 🔍 故障排查

### 问题1: Cursor中看不到mingli服务器

**解决方案**:
1. 确认已完全重启Cursor（Cmd+Q退出后重开）
2. 检查配置文件：
   ```bash
   cat ~/.cursor/mcp.json
   ```
3. 验证JSON格式：
   ```bash
   python3 -m json.tool ~/.cursor/mcp.json
   ```

### 问题2: 工具调用失败

**解决方案**:
1. 检查Python环境：
   ```bash
   /Users/lix18854/Documents/code/ziwei_mcp/venv/bin/python --version
   ```
2. 检查依赖安装：
   ```bash
   /Users/lix18854/Documents/code/ziwei_mcp/venv/bin/python -c "from py_iztro import Astro; print('OK')"
   ```
3. 手动测试MCP服务：
   ```bash
   cd /Users/lix18854/Documents/code/ziwei_mcp
   ./venv/bin/python mingli_mcp.py
   # 然后输入（按回车发送）：
   {"jsonrpc":"2.0","method":"initialize","params":{},"id":1}
   ```

### 问题3: 查看日志

**位置**:
- Cursor日志: `~/.cursor/logs/`
- MCP服务日志: 在Cursor Developer Console中查看

**启用调试日志**:
编辑 `~/.cursor/mcp.json`，修改：
```json
"env": {
  "LOG_LEVEL": "DEBUG",  // 改为DEBUG
  "DEFAULT_LANGUAGE": "zh-CN"
}
```

## 📊 当前MCP服务器列表

你的Cursor现在配置了3个MCP服务器：

1. **dataworks** - DataWorks数据开发
2. **chrome-devtools** - Chrome开发者工具
3. **mingli** ✨ - 紫微命理服务（新增）

## 💡 使用技巧

### 时辰对照表
```
0  = 早子时 (23:00-01:00)
1  = 丑时   (01:00-03:00)
2  = 寅时   (03:00-05:00)
3  = 卯时   (05:00-07:00)
4  = 辰时   (07:00-09:00)
5  = 巳时   (09:00-11:00)
6  = 午时   (11:00-13:00)
7  = 未时   (13:00-15:00)
8  = 申时   (15:00-17:00)
9  = 酉时   (17:00-19:00)
10 = 戌时   (19:00-21:00)
11 = 亥时   (21:00-23:00)
12 = 晚子时 (23:00-01:00)
```

### 推荐用法

**基础排盘**:
```
排盘：1989-10-17，午时（6），男
```

**查看运势**:
```
查询上面这个人今天的运势
```

**分析宫位**:
```
详细分析命宫
```

**使用农历**:
```
农历排盘：2000年7月17日，寅时，女
```

## 📚 更多信息

- **完整文档**: [README.md](README.md)
- **快速开始**: [QUICKSTART.md](QUICKSTART.md)
- **架构设计**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **项目总结**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

## ✨ 配置完成

**你现在可以在Cursor中使用紫微命理MCP服务了！**

记得：
1. ✅ 完全重启Cursor
2. ✅ 在聊天中输入 `mcp list` 验证
3. ✅ 尝试排一个紫微盘

🔮 **开始你的命理探索之旅！**
