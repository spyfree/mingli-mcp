# 真太阳时使用指南

**真太阳时（True Solar Time）**是根据出生地经度修正后的地方时间，可以提供更精确的时辰计算，特别适合中国西北地区（如新疆、西藏）出生的人。

---

## 📌 什么是真太阳时？

### 为什么需要真太阳时？

中国统一使用**北京时间**（东八区，UTC+8，标准经度120°E），但由于中国地域辽阔，东西跨度大（约60个经度），实际各地的地方时与北京时间存在较大差异：

| 地区 | 经度 | 与北京时间时差 | 影响 |
|------|------|----------------|------|
| **乌鲁木齐** | 87.6°E | **慢约130分钟** | ⚠️ 可能改变时辰 |
| **拉萨** | 91.1°E | **慢约116分钟** | ⚠️ 可能改变时辰 |
| 兰州 | 103.8°E | 慢约65分钟 | ⚠️ 边界可能影响 |
| 北京 | 116.4°E | 慢14分钟 | ✓ 基本不影响 |
| 上海 | 121.5°E | 快6分钟 | ✓ 基本不影响 |

### 计算原理

```
真太阳时 = 北京时间 + (出生地经度 - 120°) × 4分钟/度
```

- 每1度经度差 = 4分钟时差
- 东经大于120°：地方时快于北京时间
- 东经小于120°：地方时慢于北京时间

---

## 🚀 快速开始

### 方法1：使用城市名（推荐）

系统内置**200+个全球主要城市**的经纬度数据，可直接通过城市名使用：

```python
from systems import get_system
from utils.solar_time import get_longitude_by_city

# 获取乌鲁木齐的经度
longitude = get_longitude_by_city("乌鲁木齐")  # 87.6

#排盘时启用真太阳时
birth_info = {
    "date": "2000-08-16",
    "time_index": 6,  # 北京时间午时（12:00）
    "gender": "女",
    "longitude": longitude,
    "use_solar_time": True,
    "birth_hour": 12,
    "birth_minute": 0
}

ziwei = get_system("ziwei")
chart = ziwei.get_chart(birth_info)

# 真太阳时会自动修正：
# 北京时间 12:00 → 真太阳时 09:50 → 巳时（序号5）⚠️ 时辰改变！
```

### 方法2：手动指定经度

如果城市不在数据库中，可以手动指定经度：

```python
birth_info = {
    "date": "2000-08-16",
    "time_index": 6,
    "gender": "女",
    "longitude": 87.6,  # 手动指定经度
    "use_solar_time": True,
    "birth_hour": 12,
    "birth_minute": 30  # 可以指定精确分钟
}
```

---

## 📊 支持的城市列表

### 查看所有支持的城市

```python
from utils.solar_time import get_major_cities_longitude

cities = get_major_cities_longitude()
print(f"支持{len(cities)}个城市")
print("中国城市：", [c for c in cities.keys() if ord(c[0]) >= 0x4e00][:10])
```

### 主要城市覆盖

#### 🇨🇳 中国（43个）
直辖市、省会、港澳台、重要城市

**示例**：
- 西北地区：乌鲁木齐、拉萨、兰州、西宁、银川
- 东部地区：北京、上海、广州、深圳
- 港澳台：香港、澳门、台北

#### 🌏 亚洲（37个）
日本、韩国、东南亚、南亚、中东

**示例**：
- 日本：东京、大阪、京都
- 韩国：首尔、釜山
- 东南亚：新加坡、曼谷、吉隆坡
- 中东：迪拜、耶路撒冷

#### 🌍 欧洲（34个）
西欧、东欧、北欧

**示例**：
- 英国：伦敦、曼彻斯特
- 法国：巴黎、马赛
- 德国：柏林、慕尼黑
- 俄罗斯：莫斯科、圣彼得堡

#### 🌎 美洲（31个）
美国、加拿大、墨西哥、南美

**示例**：
- 美国：纽约、洛杉矶、旧金山、芝加哥
- 加拿大：多伦多、温哥华
- 南美：圣保罗、布宜诺斯艾利斯

#### 🌏 大洋洲（9个）
澳大利亚、新西兰

**示例**：
- 澳大利亚：悉尼、墨尔本、布里斯班
- 新西兰：奥克兰、惠灵顿

#### 🌍 非洲（5个）
主要城市

**示例**：
- 埃及：开罗
- 南非：约翰内斯堡、开普敦

**总计：200+个全球主要城市**

---

## 💡 使用示例

### 示例1：乌鲁木齐出生（时辰改变）

```python
from systems import get_system
from utils.solar_time import get_longitude_by_city

# 出生信息：2000年8月16日，北京时间12:00（午时），女性，乌鲁木齐
longitude = get_longitude_by_city("乌鲁木齐")  # 87.6

birth_info = {
    "date": "2000-08-16",
    "time_index": 6,  # 北京时间午时
    "gender": "女",
    "longitude": longitude,
    "use_solar_time": True,
    "birth_hour": 12,
    "birth_minute": 0
}

ziwei = get_system("ziwei")
chart = ziwei.get_chart(birth_info)

# 真太阳时修正结果：
# 北京时间：12:00（午时）
# 真太阳时：09:50（巳时）⚠️ 时辰改变！
# 时差：-130分钟
```

### 示例2：北京出生（时辰不变）

```python
longitude = get_longitude_by_city("北京")  # 116.4

birth_info = {
    "date": "2000-08-16",
    "time_index": 6,
    "gender": "女",
    "longitude": longitude,
    "use_solar_time": True,
    "birth_hour": 12,
    "birth_minute": 0
}

# 真太阳时修正结果：
# 北京时间：12:00（午时）
# 真太阳时：11:46（午时）✓ 时辰不变
# 时差：-14分钟
```

### 示例3：查看真太阳时详细信息

```python
from core.birth_info import BirthInfo

info = BirthInfo(
    date="2000-08-16",
    time_index=6,
    gender="女",
    longitude=87.6,  # 乌鲁木齐
    use_solar_time=True,
    birth_hour=12,
    birth_minute=0
)

# 查看真太阳时信息
print(info.get_solar_time_info())

# 输出：
# 北京时间: 2000-08-16 12:00
# 出生地经度: 87.6°E
# 时差: -130分钟
# 真太阳时: 2000-08-16 09:50
# 修正前时辰: 午时 (序号: 6)
# 修正后时辰: 巳时 (序号: 5)

# 获取修正后的时辰序号
adjusted_index = info.get_adjusted_time_index()
print(f"修正后时辰序号：{adjusted_index}")  # 5
```

### 示例4：国际城市（纽约）

```python
longitude = get_longitude_by_city("纽约")  # -74.0（西经）

birth_info = {
    "date": "2000-08-16",
    "time_index": 6,
    "gender": "女",
    "longitude": longitude,
    "use_solar_time": True,
    "birth_hour": 12,
    "birth_minute": 0
}

# 注意：虽然支持国际城市，但命理计算仍基于北京时间
# 此功能主要用于海外华人使用中国命理系统
```

---

## 🎯 何时应该启用真太阳时？

### ✅ 强烈建议启用

1. **西北地区出生**
   - 新疆（乌鲁木齐、喀什等）
   - 西藏（拉萨、日喀则等）
   - 甘肃西部（酒泉、嘉峪关等）

2. **出生时刻接近时辰边界**
   - 如11:00-13:00之间（午时边界）
   - 如23:00-01:00之间（子时边界）

3. **追求最高精度**
   - 专业命理研究
   - 重要决策参考

### 🔸 可选启用

1. **东部沿海地区**
   - 时差较小，影响不大
   - 如有精确出生时间，建议启用

2. **中部地区**
   - 时差适中
   - 接近时辰边界时建议启用

### ⚪ 无需启用

1. **不知道准确出生时间**
   - 只知道大概时辰
   - 出生时间不确定

2. **不追求极致精度**
   - 休闲娱乐用途
   - 粗略参考

---

## ⚙️ 高级用法

### 批量查询不同城市

```python
from utils.solar_time import get_longitude_by_city, format_solar_time_info
from datetime import datetime

beijing_time = datetime(2000, 8, 16, 12, 0)
cities = ["北京", "上海", "乌鲁木齐", "拉萨"]

for city in cities:
    longitude = get_longitude_by_city(city)
    info = format_solar_time_info(beijing_time, longitude, city)
    print(f"\n{info}")
    print("-" * 50)
```

### 自定义经度查询

```python
from utils.solar_time import calculate_solar_time_offset

# 计算任意经度的时差
longitude = 100.0  # 昆明附近
offset = calculate_solar_time_offset(longitude)
print(f"经度{longitude}°E，时差：{offset}分钟")
```

### 与BaZi系统配合使用

```python
bazi = get_system("bazi")

birth_info = {
    "date": "2000-08-16",
    "time_index": 6,
    "gender": "女",
    "longitude": 87.6,
    "use_solar_time": True,
    "birth_hour": 12,
    "birth_minute": 0
}

# 获取八字排盘（会自动应用真太阳时修正）
chart = bazi.get_chart(birth_info)
print(chart)

# 获取五行分析
elements = bazi.analyze_element(birth_info)
print(elements)
```

---

## ⚠️ 注意事项

### 1. 时区说明

- ✅ 真太阳时修正的是**时辰偏差**，不是时区转换
- ✅ 输入的日期时间应该是**北京时间**
- ⚠️ 如果出生地使用其他时区，需要先转换为北京时间

### 2. 精度要求

- ✅ 经度精度：保留1位小数即可（±0.1°约等于±24秒）
- ✅ 时间精度：分钟级精度足够（时辰以2小时为单位）
- ⚠️ 如果不提供 `birth_hour` 和 `birth_minute`，系统将使用时辰中点（如午时用12:00）

### 3. 数据范围

- ✅ 经度范围：-180° 到 +180°
- ✅ 纬度范围：-90° 到 +90°（当前仅用于数据记录）
- ✅ 日期范围：1900-2100年（受农历库限制）

### 4. 兼容性

- ✅ 完全向后兼容：默认不启用真太阳时
- ✅ 可选功能：`use_solar_time=False` 时行为不变
- ✅ 所有系统支持：紫微斗数、八字均已集成

---

## 🐛 故障排查

### 问题1：城市不在数据库中

**症状**：
```
ValueError: 城市 'XXX' 不在数据库中
```

**解决方案**：
```python
# 方案1：查看支持的城市列表
from utils.solar_time import get_major_cities_longitude
cities = get_major_cities_longitude()
print(sorted(cities.keys()))

# 方案2：使用附近的城市
longitude = get_longitude_by_city("最近的大城市")

# 方案3：手动指定经度（可通过Google Maps查询）
birth_info["longitude"] = 经度值
```

### 问题2：启用真太阳时但未提供经度

**症状**：
```
ValueError: 使用真太阳时必须提供经度（longitude）
```

**解决方案**：
```python
# 必须同时提供 longitude 和 use_solar_time
birth_info = {
    "longitude": 87.6,  # 必需
    "use_solar_time": True,
    ...
}
```

### 问题3：时辰没有改变

**可能原因**：
1. 经度差不大，时差未超过1小时
2. 出生时刻在时辰中段，未触及边界

**验证方法**：
```python
info = BirthInfo(..., use_solar_time=True)
print(info.get_solar_time_info())  # 查看详细信息
```

---

## 📚 参考资料

### 技术原理
- **地方时计算**：[真太阳时维基百科](https://zh.wikipedia.org/wiki/太阳时)
- **经纬度系统**：WGS84坐标系
- **时辰划分**：中国传统十二时辰

### 相关文档
- [快速开始指南](QUICK_START.md) - 基础使用
- [用户指南](USER_GUIDE.md) - 完整功能
- [API示例](API_EXAMPLES.md) - 代码示例
- [故障排查](TROUBLESHOOTING.md) - 常见问题

### 代码文件
- `utils/solar_time.py` - 真太阳时计算核心
- `core/birth_info.py` - 数据模型（支持真太阳时）
- `tests/test_solar_time.py` - 完整测试用例

---

## 💬 常见问题

### Q1：真太阳时和北京时间有什么区别？

**A**：北京时间是统一的标准时间（UTC+8），而真太阳时是根据出生地经度计算的地方时。例如乌鲁木齐（87.6°E）的真太阳时比北京时间慢约130分钟。

### Q2：我应该使用真太阳时吗？

**A**：
- **西北地区（如新疆、西藏）**：强烈建议使用
- **东部地区（如北京、上海）**：影响不大，可选
- **不确定出生时间**：无需使用

### Q3：系统支持哪些城市？

**A**：内置200+个全球主要城市，包括：
- 中国43个城市（全部省会+重要城市+港澳台）
- 亚洲37个城市（日韩、东南亚、南亚、中东）
- 欧洲34个城市（西欧、东欧、北欧）
- 美洲31个城市（美国、加拿大、南美）
- 大洋洲9个城市（澳大利亚、新西兰）
- 非洲5个城市（埃及、南非等）

### Q4：如何查询城市的经度？

**A**：
```python
from utils.solar_time import get_longitude_by_city

# 方法1：通过城市名查询
longitude = get_longitude_by_city("乌鲁木齐")

# 方法2：查看所有支持的城市
from utils.solar_time import get_major_cities_longitude
cities = get_major_cities_longitude()
print(cities)
```

### Q5：真太阳时会改变日期吗？

**A**：不会。真太阳时只修正时辰，不改变日期。即使时差达到2小时，也只在时辰边界附近可能改变时辰序号。

### Q6：纬度参数有什么用？

**A**：当前纬度参数仅用于数据记录，暂未用于计算。保留此字段是为了未来可能的扩展功能（如考虑地理纬度对命理的影响）。

---

**提示**：如有其他问题，请参考 [故障排查指南](TROUBLESHOOTING.md) 或在GitHub提交Issue。

**版本**：1.0.14+ | **更新日期**：2025-01 | **状态**：✅ 稳定版
