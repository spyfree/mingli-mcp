# 快速开始指南

## 🚀 5分钟快速上手

### 步骤1: 安装依赖

```bash
cd /Users/lix18854/Documents/code/ziwei_mcp

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 步骤2: 测试功能

```bash
# 运行测试脚本验证安装
python tests/test_ziwei.py
```

如果看到 "🎉 所有测试通过！"，说明安装成功。

### 步骤3: 配置 Cursor

编辑 `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "mingli": {
      "command": "/Users/lix18854/Documents/code/ziwei_mcp/venv/bin/python",
      "args": ["/Users/lix18854/Documents/code/ziwei_mcp/mingli_mcp.py"],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 步骤4: 重启 Cursor

重启 Cursor IDE，你应该能在工具列表中看到：
- get_ziwei_chart
- get_ziwei_fortune
- analyze_ziwei_palace
- list_fortune_systems

### 步骤5: 开始使用

在 Cursor 中尝试：

```
帮我排一个紫微斗数盘：1989年10月17日，午时，男性
```

## 📝 常用命令示例

### 排盘
```
排一个紫微命盘：2000年8月16日，寅时，女性
```

### 查询运势
```
查询2000年8月16日寅时出生的女性，今天的运势
```

### 分析宫位
```
分析上面这个人的命宫
```

### 使用农历
```
排盘：农历2000年7月17日，寅时，女性
```

## 🔧 故障排查

### 问题1: py-iztro 安装失败

```bash
# 尝试升级pip
pip install --upgrade pip

# 重新安装
pip install py-iztro
```

### 问题2: Cursor 无法连接

1. 检查 mcp.json 中的路径是否正确
2. 确保 mingli_mcp.py 有执行权限: `chmod +x mingli_mcp.py`
3. 查看 Cursor 日志: `~/.cursor/logs/`

### 问题3: 测试失败

```bash
# 确保在虚拟环境中
source venv/bin/activate

# 检查Python版本（需要3.8+）
python --version

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

## 📚 更多信息

- 完整文档: [README.md](README.md)
- 项目结构说明: [README.md#项目结构](README.md#-项目结构)
- 扩展新系统: [README.md#扩展新命理系统](README.md#-扩展新命理系统)

## 💡 提示

1. **时辰对照表**:
   - 子时(23-01): 0 或 12
   - 丑时(01-03): 1
   - 寅时(03-05): 2
   - 卯时(05-07): 3
   - 辰时(07-09): 4
   - 巳时(09-11): 5
   - 午时(11-13): 6
   - 未时(13-15): 7
   - 申时(15-17): 8
   - 酉时(17-19): 9
   - 戌时(19-21): 10
   - 亥时(21-23): 11

2. **历法选择**:
   - 推荐使用阳历（公历），更准确且易于使用
   - 如果只知道农历，可以先转换为阳历

3. **输出格式**:
   - markdown: 易读的格式化输出（默认）
   - json: 结构化数据，便于程序处理

---

**开始你的命理探索之旅！** 🔮
