# 快速开始指南

欢迎使用 **Mingli MCP Server**！本指南将帮助您在 5 分钟内开始使用。

---

## 📋 目录

- [1. 安装](#1-安装)
- [2. 配置](#2-配置)
- [3. 第一次排盘](#3-第一次排盘)
- [4. 常见用法](#4-常见用法)
- [5. 下一步](#5-下一步)

---

## 1. 安装

### 方式 A: uvx（推荐，最简单）

```bash
# 一条命令搞定
uvx mingli-mcp
```

### 方式 B: pip 安装

```bash
# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 安装
pip install mingli-mcp
```

### 方式 C: Docker

```bash
docker pull ghcr.io/spyfree/mingli-mcp:latest
docker run -p 8080:8080 ghcr.io/spyfree/mingli-mcp
```

---

## 2. 配置

### 在 Cursor IDE 中配置

编辑或创建 `~/.cursor/mcp.json`：

```json
{
  "mcpServers": {
    "mingli": {
      "command": "uvx",
      "args": ["mingli-mcp"],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 在 Claude Desktop 中配置

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "mingli": {
      "command": "uvx",
      "args": ["mingli-mcp"]
    }
  }
}
```

**重启应用**以加载配置。

---

## 3. 第一次排盘

### 🔮 紫微斗数排盘

在 Cursor 或 Claude Desktop 中，输入：

```
帮我排一个紫微斗数盘：
- 出生日期：2000年8月16日
- 出生时辰：寅时（凌晨3-5点）
- 性别：女
```

您将看到包含十二宫、主星、四化的完整排盘！

### 🎴 八字排盘

```
帮我算八字：
- 出生日期：1990年5月20日
- 出生时辰：午时（中午11-13点）
- 性别：男
```

---

## 4. 常见用法

### 查询运势

```
查询2000年8月16日寅时出生的女性，今天的紫微运势
```

### 分析宫位

```
分析上面这个人的命宫
```

### 五行分析

```
帮我看看1995年7月10日申时男性的五行缺什么
```

### 使用农历

```
排盘：农历1995年7月初七，酉时，女性
```

### 多语言输出

```
请用英语排紫微盘：2000-08-16，寅时，女
```

支持的语言：
- 🇨🇳 简体中文 (zh-CN)
- 🇹🇼 繁体中文 (zh-TW)
- 🇺🇸 English (en-US)
- 🇯🇵 日本語 (ja-JP)
- 🇰🇷 한국어 (ko-KR)
- 🇻🇳 Tiếng Việt (vi-VN)

---

## 5. 下一步

### 🎓 深入学习

- [用户指南](USER_GUIDE.md) - 完整功能说明
- [API 文档](API_EXAMPLES.md) - 编程接口
- [故障排查](TROUBLESHOOTING.md) - 常见问题

### 🛠️ 进阶配置

- [环境变量配置](../CLAUDE.md#配置说明)
- [HTTP 模式](../README.md#方式2-docker)
- [自定义日志级别](TROUBLESHOOTING.md#调试模式)

### 🤝 获取帮助

- [GitHub Issues](https://github.com/spyfree/mingli-mcp/issues)
- [讨论区](https://github.com/spyfree/mingli-mcp/discussions)

---

## 💡 小贴士

### 时辰对照表

| 时辰 | 时间 | 序号 |
|------|------|------|
| 早子时 | 23:00-01:00 | 0 |
| 丑时 | 01:00-03:00 | 1 |
| 寅时 | 03:00-05:00 | 2 |
| 卯时 | 05:00-07:00 | 3 |
| 辰时 | 07:00-09:00 | 4 |
| 巳时 | 09:00-11:00 | 5 |
| 午时 | 11:00-13:00 | 6 |
| 未时 | 13:00-15:00 | 7 |
| 申时 | 15:00-17:00 | 8 |
| 酉时 | 17:00-19:00 | 9 |
| 戌时 | 19:00-21:00 | 10 |
| 亥时 | 21:00-23:00 | 11 |
| 晚子时 | 23:00-01:00 | 12 |

### 性别说明

- **男** - 男性
- **女** - 女性

### 历法说明

- **阳历**（solar）- 公历，默认选项
- **农历**（lunar）- 中国传统历法
- **闰月** - 农历特有，需明确指定

---

## ⚡ 快速命令参考

```bash
# 查看服务器状态
curl http://localhost:8080/health

# 查看可用系统
# 在 AI 助手中输入："列出所有可用的命理系统"

# 设置调试模式
export LOG_LEVEL=DEBUG
mingli-mcp

# 查看版本
pip show mingli-mcp
```

---

**🎉 开始探索命理世界吧！**
