# API 使用示例

本文档提供丰富的代码示例，帮助您通过编程方式使用 Mingli MCP Server。

---

## 📋 目录

- [基础用法](#基础用法)
- [紫微斗数示例](#紫微斗数示例)
- [八字系统示例](#八字系统示例)
- [高级示例](#高级示例)
- [错误处理](#错误处理)
- [性能优化](#性能优化)

---

## 基础用法

### 安装和导入

```python
# 安装
# pip install mingli-mcp

# 导入
from systems import get_system, list_systems
from datetime import datetime
```

### 列出可用系统

```python
# 获取所有注册的命理系统
systems = list_systems()
print(f"可用系统: {systems}")
# 输出: ['ziwei', 'bazi']

# 获取系统实例
ziwei = get_system('ziwei')
bazi = get_system('bazi')

# 查看系统信息
print(f"系统名称: {ziwei.get_system_name()}")  # 紫微斗数
print(f"系统版本: {ziwei.get_system_version()}")  # 0.3.3
print(f"支持功能: {ziwei.get_capabilities()}")
```

---

## 紫微斗数示例

### 示例 1: 基础排盘

```python
from systems import get_system

# 获取紫微系统
ziwei = get_system('ziwei')

# 准备生辰信息
birth_info = {
    'date': '2000-08-16',  # 出生日期
    'time_index': 2,        # 寅时
    'gender': '女',         # 性别
    'calendar': 'solar'     # 阳历（默认）
}

# 获取排盘
chart = ziwei.get_chart(birth_info)

# 打印基本信息
print(f"阳历: {chart['basic_info']['阳历日期']}")
print(f"农历: {chart['basic_info']['农历日期']}")
print(f"命主: {chart['basic_info']['命主']}")
print(f"身主: {chart['basic_info']['身主']}")

# 打印宫位信息
for palace in chart['palaces']:
    print(f"\n{palace['name']}:")
    print(f"  天干: {palace['heavenly_stem']}")
    print(f"  地支: {palace['earthly_branch']}")
    print(f"  主星: {', '.join(palace.get('major_stars', []))}")
```

### 示例 2: 多语言排盘

```python
# 简体中文（默认）
chart_cn = ziwei.get_chart(birth_info, language='zh-CN')

# 繁体中文
chart_tw = ziwei.get_chart(birth_info, language='zh-TW')

# 英文
chart_en = ziwei.get_chart(birth_info, language='en-US')

# 日文
chart_jp = ziwei.get_chart(birth_info, language='ja-JP')

print("英文宫位名:", chart_en['palaces'][0]['name'])
```

### 示例 3: 运势查询

```python
from datetime import datetime

birth_info = {
    'date': '2000-08-16',
    'time_index': 2,
    'gender': '女',
}

# 查询今天的运势
fortune_today = ziwei.get_fortune(birth_info, datetime.now())

print(f"查询日期: {fortune_today['query_date']}")
print(f"当前大限: {fortune_today['decadal']['palace']}")
print(f"流年: {fortune_today['yearly']['heavenly_stem']}{fortune_today['yearly']['earthly_branch']}")

# 查询特定日期的运势
query_date = datetime(2025, 12, 31)
fortune_future = ziwei.get_fortune(birth_info, query_date)
```

### 示例 4: 宫位分析

```python
# 分析命宫
ming_analysis = ziwei.analyze_palace(birth_info, '命宫')

print(f"宫位: {ming_analysis['palace_name']}")
print(f"干支: {ming_analysis['heavenly_stem']}{ming_analysis['earthly_branch']}")
print(f"主星: {', '.join(ming_analysis.get('major_stars', []))}")

# 批量分析多个宫位
palaces_to_analyze = ['命宫', '夫妻宫', '财帛宫', '官禄宫']

for palace_name in palaces_to_analyze:
    analysis = ziwei.analyze_palace(birth_info, palace_name)
    print(f"\n{palace_name}:")
    print(f"  主星: {', '.join(analysis.get('major_stars', []))}")
```

### 示例 5: 农历排盘

```python
# 农历生日
lunar_birth = {
    'date': '2000-07-17',  # 农历日期
    'time_index': 2,
    'gender': '女',
    'calendar': 'lunar',
    'is_leap_month': False  # 是否闰月
}

chart = ziwei.get_chart(lunar_birth)
print(f"农历: {chart['basic_info']['农历日期']}")
print(f"对应阳历: {chart['basic_info']['阳历日期']}")

# 闰月示例
leap_month_birth = {
    'date': '1995-08-20',  # 农历闰八月二十
    'time_index': 6,
    'gender': '男',
    'calendar': 'lunar',
    'is_leap_month': True  # 闰月
}

chart_leap = ziwei.get_chart(leap_month_birth)
```

---

## 八字系统示例

### 示例 6: 八字排盘

```python
from systems import get_system

# 获取八字系统
bazi = get_system('bazi')

# 准备生辰信息
birth_info = {
    'date': '1990-05-20',
    'time_index': 6,  # 午时
    'gender': '男',
}

# 获取排盘
chart = bazi.get_chart(birth_info)

# 打印基本信息
print(f"阳历: {chart['solar_date']}")
print(f"农历: {chart['lunar_date']}")
print(f"生肖: {chart['zodiac']}")
print(f"八字: {chart['eight_char']}")
print(f"日主: {chart['day_master']}")

# 打印四柱
for pillar_name, pillar_data in chart['pillars'].items():
    print(f"\n{pillar_name}柱: {pillar_data['pillar']}")
    print(f"  天干: {pillar_data['gan']} ({pillar_data['gan_wu_xing']})")
    print(f"  地支: {pillar_data['zhi']} ({pillar_data['zhi_wu_xing']})")
    print(f"  十神: {pillar_data['shi_shen']}")

# 打印十神统计
print("\n十神分布:")
for deity_name, deity_data in chart['deities'].items():
    print(f"  {deity_name}: {deity_data}")
```

### 示例 7: 五行分析

```python
# 分析五行
element_analysis = bazi.analyze_element(birth_info)

print(f"日主: {element_analysis['day_master']}")
print(f"日主五行: {element_analysis['day_master_element']}")

# 五行分数
print("\n五行分数:")
for element, score in element_analysis['scores'].items():
    percentage = element_analysis['percentages'][element]
    print(f"  {element}: {score} ({percentage:.1f}%)")

# 最旺和最弱
print(f"\n最旺五行: {element_analysis['strongest']['element']} ({element_analysis['strongest']['score']})")
print(f"最弱五行: {element_analysis['weakest']['element']} ({element_analysis['weakest']['score']})")

# 缺失五行
if element_analysis['missing']:
    print(f"缺失五行: {', '.join(element_analysis['missing'])}")
else:
    print("五行齐全")

# 平衡度
print(f"平衡度: {element_analysis['balance']}/100")
```

### 示例 8: 八字运势

```python
from datetime import datetime

birth_info = {
    'date': '1990-05-20',
    'time_index': 6,
    'gender': '男',
}

# 获取运势
fortune = bazi.get_fortune(birth_info, datetime.now())

print(f"当前年龄: {fortune['age']}岁")

# 大运信息
da_yun = fortune['da_yun']
print(f"\n大运: {da_yun['description']}")
print(f"年龄范围: {da_yun['age_range']}")
print(f"干支: {da_yun['gan_zhi']}")

# 流年信息
liu_nian = fortune['liu_nian']
print(f"\n流年: {liu_nian['year']}年")
print(f"干支: {liu_nian['gan_zhi']}")
print(f"生肖: {liu_nian['zodiac']}")
```

---

## 高级示例

### 示例 9: 批量处理

```python
from systems import get_system

ziwei = get_system('ziwei')

# 批量数据
people_data = [
    {'name': '张三', 'date': '2000-08-16', 'time_index': 2, 'gender': '女'},
    {'name': '李四', 'date': '1990-05-20', 'time_index': 6, 'gender': '男'},
    {'name': '王五', 'date': '1985-03-15', 'time_index': 4, 'gender': '女'},
]

# 批量排盘
results = []
for person in people_data:
    name = person.pop('name')  # 移除name，保留birth_info
    try:
        chart = ziwei.get_chart(person)
        results.append({
            'name': name,
            'chart': chart,
            'status': 'success'
        })
    except Exception as e:
        results.append({
            'name': name,
            'error': str(e),
            'status': 'error'
        })

# 输出结果
for result in results:
    if result['status'] == 'success':
        print(f"{result['name']}: 排盘成功")
    else:
        print(f"{result['name']}: 排盘失败 - {result['error']}")
```

### 示例 10: 自定义合盘

```python
def compatibility_analysis(person1, person2):
    """简单的合盘分析"""
    ziwei = get_system('ziwei')

    # 获取两人的排盘
    chart1 = ziwei.get_chart(person1)
    chart2 = ziwei.get_chart(person2)

    # 获取夫妻宫信息
    palace1 = next(p for p in chart1['palaces'] if p['name'] == '夫妻宫')
    palace2 = next(p for p in chart2['palaces'] if p['name'] == '夫妻宫')

    # 简单比较（实际应用中需要更复杂的逻辑）
    compatibility_score = 0

    # 比较主星
    stars1 = set(palace1.get('major_stars', []))
    stars2 = set(palace2.get('major_stars', []))
    common_stars = stars1 & stars2

    if common_stars:
        compatibility_score += 20

    # 比较干支
    if palace1['heavenly_stem'] == palace2['heavenly_stem']:
        compatibility_score += 15

    if palace1['earthly_branch'] == palace2['earthly_branch']:
        compatibility_score += 15

    return {
        'score': compatibility_score,
        'person1_palace': palace1,
        'person2_palace': palace2,
        'common_stars': list(common_stars)
    }

# 使用
person1 = {'date': '2000-08-16', 'time_index': 2, 'gender': '女'}
person2 = {'date': '1999-06-15', 'time_index': 8, 'gender': '男'}

result = compatibility_analysis(person1, person2)
print(f"合盘得分: {result['score']}/100")
```

### 示例 11: JSON 格式输出

```python
import json
from systems import get_system

ziwei = get_system('ziwei')

birth_info = {
    'date': '2000-08-16',
    'time_index': 2,
    'gender': '女',
}

# 获取 JSON 格式数据
chart = ziwei.get_chart(birth_info)

# 保存到文件
with open('chart_2000-08-16.json', 'w', encoding='utf-8') as f:
    json.dump(chart, f, ensure_ascii=False, indent=2)

# 从文件读取
with open('chart_2000-08-16.json', 'r', encoding='utf-8') as f:
    loaded_chart = json.load(f)

print("排盘数据已保存到 chart_2000-08-16.json")
```

### 示例 12: 运势追踪

```python
from datetime import datetime, timedelta
from systems import get_system

ziwei = get_system('ziwei')

birth_info = {
    'date': '2000-08-16',
    'time_index': 2,
    'gender': '女',
}

# 追踪未来12个月的流月
print("未来12个月运势:")
for i in range(12):
    query_date = datetime.now() + timedelta(days=30 * i)
    fortune = ziwei.get_fortune(birth_info, query_date)

    month = query_date.strftime('%Y-%m')
    liu_yue = fortune.get('monthly', {})

    print(f"\n{month}:")
    if liu_yue:
        print(f"  流月宫: {liu_yue.get('palace', 'N/A')}")
        print(f"  干支: {liu_yue.get('heavenly_stem', '')}{liu_yue.get('earthly_branch', '')}")
```

---

## 错误处理

### 示例 13: 完整错误处理

```python
from systems import get_system
from core.exceptions import (
    ValidationError,
    DateRangeError,
    SystemError,
    SystemNotFoundError,
    LanguageNotSupportedError,
)

def safe_get_chart(birth_info, language='zh-CN'):
    """带完整错误处理的排盘函数"""
    try:
        ziwei = get_system('ziwei')
        chart = ziwei.get_chart(birth_info, language)
        return {'status': 'success', 'data': chart}

    except SystemNotFoundError as e:
        return {'status': 'error', 'type': 'system_not_found', 'message': str(e)}

    except DateRangeError as e:
        return {'status': 'error', 'type': 'date_range', 'message': str(e)}

    except ValidationError as e:
        return {'status': 'error', 'type': 'validation', 'message': str(e)}

    except LanguageNotSupportedError as e:
        return {'status': 'error', 'type': 'language', 'message': str(e)}

    except SystemError as e:
        return {'status': 'error', 'type': 'system', 'message': str(e)}

    except Exception as e:
        return {'status': 'error', 'type': 'unknown', 'message': str(e)}

# 使用
result = safe_get_chart({
    'date': '2000-08-16',
    'time_index': 2,
    'gender': '女'
})

if result['status'] == 'success':
    print("排盘成功")
    chart = result['data']
else:
    print(f"排盘失败: {result['type']} - {result['message']}")
```

### 示例 14: 参数验证

```python
from utils.validators import (
    validate_date,
    validate_date_range,
    validate_time_index,
    validate_gender,
    validate_language,
)
from core.exceptions import ValidationError

def validate_birth_info(birth_info):
    """验证生辰信息的完整性和有效性"""
    errors = []

    # 验证日期
    if 'date' not in birth_info:
        errors.append("缺少日期字段")
    elif not validate_date(birth_info['date']):
        errors.append(f"无效的日期格式: {birth_info['date']}")
    else:
        try:
            validate_date_range(birth_info['date'])
        except ValidationError as e:
            errors.append(str(e))

    # 验证时辰
    if 'time_index' not in birth_info:
        errors.append("缺少时辰字段")
    elif not validate_time_index(birth_info['time_index']):
        errors.append(f"无效的时辰: {birth_info['time_index']}")

    # 验证性别
    if 'gender' not in birth_info:
        errors.append("缺少性别字段")
    elif not validate_gender(birth_info['gender']):
        errors.append(f"无效的性别: {birth_info['gender']}")

    # 验证语言（如果提供）
    if 'language' in birth_info:
        try:
            validate_language(birth_info['language'])
        except ValidationError as e:
            errors.append(str(e))

    if errors:
        raise ValidationError(f"参数验证失败: {'; '.join(errors)}")

    return True

# 使用
try:
    validate_birth_info({
        'date': '2000-08-16',
        'time_index': 2,
        'gender': '女'
    })
    print("参数验证通过")
except ValidationError as e:
    print(f"验证失败: {e}")
```

---

## 性能优化

### 示例 15: 使用性能监控

```python
from utils.performance import PerformanceTimer, log_performance

# 方式1: 装饰器
@log_performance
def batch_chart_generation(people_data):
    """批量生成排盘"""
    ziwei = get_system('ziwei')
    return [ziwei.get_chart(person) for person in people_data]

# 方式2: 上下文管理器
def analyze_with_timing():
    with PerformanceTimer("批量排盘") as timer:
        ziwei = get_system('ziwei')
        charts = []
        for i in range(10):
            birth_info = {
                'date': f'2000-0{i+1}-01',
                'time_index': i,
                'gender': '女' if i % 2 == 0 else '男'
            }
            charts.append(ziwei.get_chart(birth_info))

    print(f"总耗时: {timer.elapsed:.3f}秒")
    print(f"平均每个: {timer.elapsed/10:.3f}秒")
    return charts

# 使用
import logging
logging.basicConfig(level=logging.DEBUG)

people = [
    {'date': '2000-08-16', 'time_index': 2, 'gender': '女'},
    {'date': '1990-05-20', 'time_index': 6, 'gender': '男'},
]

charts = batch_chart_generation(people)
```

### 示例 16: 缓存优化

```python
from functools import lru_cache
import json

class ChartCache:
    """排盘结果缓存"""

    @staticmethod
    @lru_cache(maxsize=128)
    def get_chart_cached(date, time_index, gender, calendar='solar'):
        """缓存版本的排盘函数"""
        ziwei = get_system('ziwei')
        birth_info = {
            'date': date,
            'time_index': time_index,
            'gender': gender,
            'calendar': calendar
        }
        return json.dumps(ziwei.get_chart(birth_info))  # 序列化以便缓存

    @staticmethod
    def get_chart(birth_info):
        """获取排盘（自动使用缓存）"""
        cached_json = ChartCache.get_chart_cached(
            birth_info['date'],
            birth_info['time_index'],
            birth_info['gender'],
            birth_info.get('calendar', 'solar')
        )
        return json.loads(cached_json)

# 使用
cache = ChartCache()

# 第一次调用 - 慢
chart1 = cache.get_chart({'date': '2000-08-16', 'time_index': 2, 'gender': '女'})

# 第二次调用相同参数 - 快（从缓存获取）
chart2 = cache.get_chart({'date': '2000-08-16', 'time_index': 2, 'gender': '女'})

# 查看缓存统计
info = ChartCache.get_chart_cached.cache_info()
print(f"缓存命中率: {info.hits}/{info.hits + info.misses}")
```

---

## 完整应用示例

### 示例 17: 命理分析报告生成器

```python
from systems import get_system
from datetime import datetime

class FortuneReport:
    """命理分析报告生成器"""

    def __init__(self, birth_info):
        self.birth_info = birth_info
        self.ziwei = get_system('ziwei')
        self.bazi = get_system('bazi')

    def generate_full_report(self):
        """生成完整报告"""
        report = {
            'basic_info': self.birth_info,
            'ziwei': self._analyze_ziwei(),
            'bazi': self._analyze_bazi(),
            'recommendations': self._generate_recommendations(),
            'generated_at': datetime.now().isoformat()
        }
        return report

    def _analyze_ziwei(self):
        """紫微分析"""
        chart = self.ziwei.get_chart(self.birth_info)
        fortune = self.ziwei.get_fortune(self.birth_info, datetime.now())

        # 分析关键宫位
        key_palaces = ['命宫', '夫妻宫', '财帛宫', '官禄宫']
        palace_analysis = {}

        for palace_name in key_palaces:
            palace_analysis[palace_name] = self.ziwei.analyze_palace(
                self.birth_info, palace_name
            )

        return {
            'chart': chart,
            'fortune': fortune,
            'key_palaces': palace_analysis
        }

    def _analyze_bazi(self):
        """八字分析"""
        chart = self.bazi.get_chart(self.birth_info)
        element_analysis = self.bazi.analyze_element(self.birth_info)

        return {
            'chart': chart,
            'element_analysis': element_analysis
        }

    def _generate_recommendations(self):
        """生成建议"""
        element_analysis = self.bazi.analyze_element(self.birth_info)

        recommendations = []

        # 根据五行缺失给建议
        if element_analysis['missing']:
            missing = element_analysis['missing']
            recommendations.append({
                'category': '五行补救',
                'content': f"建议补{', '.join(missing)}：可穿相应颜色衣服、佩戴相关材质饰品"
            })

        # 根据平衡度给建议
        balance = element_analysis['balance']
        if balance < 50:
            recommendations.append({
                'category': '五行平衡',
                'content': '五行偏枯，建议注意身体健康，保持心态平和'
            })

        return recommendations

    def export_markdown(self, filename):
        """导出为Markdown文件"""
        report = self.generate_full_report()

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# 命理分析报告\n\n")
            f.write(f"生成时间: {report['generated_at']}\n\n")

            # 基本信息
            f.write(f"## 基本信息\n\n")
            f.write(f"- 出生日期: {self.birth_info['date']}\n")
            f.write(f"- 性别: {self.birth_info['gender']}\n\n")

            # 八字五行
            f.write(f"## 八字五行\n\n")
            ea = report['bazi']['element_analysis']
            f.write(f"日主: {ea['day_master']} ({ea['day_master_element']})\n\n")

            # 建议
            f.write(f"## 建议\n\n")
            for rec in report['recommendations']:
                f.write(f"### {rec['category']}\n\n")
                f.write(f"{rec['content']}\n\n")

        print(f"报告已导出到: {filename}")

# 使用
birth_info = {
    'date': '2000-08-16',
    'time_index': 2,
    'gender': '女'
}

report_generator = FortuneReport(birth_info)
report_generator.export_markdown('fortune_report.md')

# 或获取JSON格式
import json
report = report_generator.generate_full_report()
print(json.dumps(report, ensure_ascii=False, indent=2))
```

---

## 下一步

- [用户指南](USER_GUIDE.md) - 详细功能说明
- [故障排查](TROUBLESHOOTING.md) - 问题解决
- [开发文档](../CLAUDE.md) - 扩展开发

---

**📖 更多示例持续添加中...**

有问题？[提交 Issue](https://github.com/spyfree/mingli-mcp/issues)
