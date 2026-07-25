"""
八字系统格式化器

用于将八字数据格式化为JSON和Markdown格式
"""

from typing import Any, Dict, Union


class BaziFormatter:
    """八字格式化器"""

    def format_chart(
        self, chart_data: Dict[str, Any], format_type: str = "json"
    ) -> Union[str, Dict[str, Any]]:
        """
        格式化八字排盘数据

        Args:
            chart_data: 排盘数据
            format_type: 格式类型 ('json' 或 'markdown')

        Returns:
            format_type="markdown" 时返回Markdown字符串，否则原样返回数据字典
        """
        if format_type == "markdown":
            return self._format_chart_markdown(chart_data)
        else:
            return chart_data

    def format_fortune(
        self, fortune_data: Dict[str, Any], format_type: str = "json"
    ) -> Union[str, Dict[str, Any]]:
        """
        格式化运势数据

        Args:
            fortune_data: 运势数据
            format_type: 格式类型

        Returns:
            format_type="markdown" 时返回Markdown字符串，否则原样返回数据字典
        """
        if format_type == "markdown":
            return self._format_fortune_markdown(fortune_data)
        else:
            return fortune_data

    def format_element_analysis(
        self, analysis_data: Dict[str, Any], format_type: str = "json"
    ) -> Union[str, Dict[str, Any]]:
        """
        格式化五行分析数据

        Args:
            analysis_data: 分析数据
            format_type: 格式类型

        Returns:
            format_type="markdown" 时返回Markdown字符串，否则原样返回数据字典
        """
        if format_type == "markdown":
            return self._format_element_markdown(analysis_data)
        else:
            return analysis_data

    # 显式返回str的Markdown入口（与ZiweiFormatter的命名保持一致）。
    # 调用方需要str时用这些方法，避免拿到Union后还得自己收窄类型。
    def format_chart_markdown(self, chart_data: Dict[str, Any]) -> str:
        """将排盘数据格式化为Markdown"""
        return self._format_chart_markdown(chart_data)

    def format_fortune_markdown(self, fortune_data: Dict[str, Any]) -> str:
        """将运势数据格式化为Markdown"""
        return self._format_fortune_markdown(fortune_data)

    def format_element_analysis_markdown(self, analysis_data: Dict[str, Any]) -> str:
        """将五行分析数据格式化为Markdown"""
        return self._format_element_markdown(analysis_data)

    def _format_chart_markdown(self, data: Dict[str, Any]) -> str:
        """格式化排盘为Markdown"""
        md = f"""# 八字排盘

## 基本信息
- **阳历**: {data['solar_date']}
- **农历**: {data['lunar_date']}
- **性别**: {data['gender']}
- **生肖**: {data['zodiac']}

## 四柱八字
```
{data['eight_char']}
```

### 详细四柱
| 柱 | 天干 | 地支 | 干支 |
|---|------|------|------|
| 年柱 | {data['pillars']['year']['gan']} | {data['pillars']['year']['zhi']} | {data['pillars']['year']['pillar']} |
| 月柱 | {data['pillars']['month']['gan']} | {data['pillars']['month']['zhi']} | {data['pillars']['month']['pillar']} |
| 日柱 | {data['pillars']['day']['gan']} | {data['pillars']['day']['zhi']} | {data['pillars']['day']['pillar']} |
| 时柱 | {data['pillars']['hour']['gan']} | {data['pillars']['hour']['zhi']} | {data['pillars']['hour']['pillar']} |

**日主**: {data['day_master']}（命主本身，以日干为准）

## 十神分析
- **年干**: {data['deities']['year_gan']}
- **月干**: {data['deities']['month_gan']}
- **日干**: {data['deities']['day_gan']}
- **时干**: {data['deities']['hour_gan']}

## 五行分析
- **分数**: {data['wu_xing']['description']}
- **详细**: 金{data['wu_xing']['scores']['金']} 木{data['wu_xing']['scores']['木']} 水{data['wu_xing']['scores']['水']} 火{data['wu_xing']['scores']['火']} 土{data['wu_xing']['scores']['土']}

## 地支藏干
- **年支** {data['pillars']['year']['zhi']}: {', '.join(data['zhi_cang_gan']['year'])}
- **月支** {data['pillars']['month']['zhi']}: {', '.join(data['zhi_cang_gan']['month'])}
- **日支** {data['pillars']['day']['zhi']}: {', '.join(data['zhi_cang_gan']['day'])}
- **时支** {data['pillars']['hour']['zhi']}: {', '.join(data['zhi_cang_gan']['hour'])}
"""

        # 藏干十神（可选：旧结构的数据没有这个字段）
        zhi_deities = data.get("zhi_deities")
        if zhi_deities:
            md += "\n## 藏干十神\n"
            for key, label in (
                ("year", "年支"),
                ("month", "月支"),
                ("day", "日支"),
                ("hour", "时支"),
            ):
                hidden = data["zhi_cang_gan"].get(key, [])
                names = zhi_deities.get(key, [])
                pairs = "、".join(f"{g}({d})" for g, d in zip(hidden, names))
                md += f"- **{label}** {data['pillars'][key]['zhi']}: {pairs}\n"

        return md

    @staticmethod
    def _format_deities(deities: Dict[str, Any]) -> str:
        """把十神信息压成一行：天干十神（藏干十神）"""
        if not deities:
            return ""

        gan = deities.get("gan", "")
        zhi = deities.get("zhi") or []
        if gan and zhi:
            return f"{gan}（藏干: {'、'.join(zhi)}）"
        return gan or "、".join(zhi)

    def _format_fortune_markdown(self, data: Dict[str, Any]) -> str:
        """格式化运势为Markdown"""
        da_yun = data.get("da_yun", {})
        liu_nian = data.get("liu_nian", {})

        md = f"""# 八字运势

## 查询信息
- **查询日期**: {data['query_date']}
- **当前年龄**: {data['age']}岁"""

        if data.get("nominal_age"):
            md += f"（虚岁 {data['nominal_age']}）"

        md += f"\n- **日主**: {data['day_master']}\n"

        # 起运信息（真实推演才有）
        qi_yun = data.get("qi_yun")
        if qi_yun:
            md += f"- **起运**: {qi_yun['description']}\n"
        if data.get("da_yun_direction"):
            md += f"- **排运方向**: {data['da_yun_direction']}\n"

        md += "\n## 当前大运\n"
        if da_yun.get("is_pre_start"):
            md += f"- **状态**: 尚未起运，当前处于小运期（{da_yun.get('age_range', '')}）\n"
        else:
            if da_yun.get("gan_zhi"):
                md += f"- **干支**: {da_yun['gan_zhi']}\n"
            md += f"- **{'年龄段' if not da_yun.get('gan_zhi') else '年龄范围'}**: "
            md += f"{da_yun.get('age_range', '')}\n"
            if da_yun.get("year_range"):
                md += f"- **公历年份**: {da_yun['year_range']}\n"
            deity_text = self._format_deities(da_yun.get("deities", {}))
            if deity_text:
                md += f"- **十神**: {deity_text}\n"
            if da_yun.get("xun_kong"):
                md += f"- **旬空**: {da_yun['xun_kong']}\n"
        if da_yun.get("description"):
            md += f"- **说明**: {da_yun['description']}\n"

        md += f"""
## 流年
- **流年**: {liu_nian.get('year', '')}年
- **干支**: {liu_nian.get('gan_zhi', '')}
- **生肖**: {liu_nian.get('zodiac', '')}
"""
        liu_nian_deities = self._format_deities(liu_nian.get("deities", {}))
        if liu_nian_deities:
            md += f"- **十神**: {liu_nian_deities}\n"

        # 大运一览表
        da_yun_list = data.get("da_yun_list") or []
        if da_yun_list:
            md += "\n## 大运一览\n\n"
            md += "| 步 | 干支 | 年龄 | 公历年份 | 十神 |\n"
            md += "|---|------|------|----------|------|\n"
            for entry in da_yun_list:
                current = "▶ " if entry is da_yun else ""
                gan_zhi = entry.get("gan_zhi") or "—"
                label = "小运" if entry.get("is_pre_start") else str(entry.get("index", ""))
                deity_text = self._format_deities(entry.get("deities", {})) or "—"
                md += (
                    f"| {current}{label} | {gan_zhi} | {entry.get('age_range', '')} "
                    f"| {entry.get('year_range', '')} | {deity_text} |\n"
                )

        md += f"""
---

## 本命八字
```
{data['basic_chart']['eight_char']}
```
"""
        return md

    def _format_element_markdown(self, data: Dict[str, Any]) -> str:
        """格式化五行分析为Markdown"""
        md = f"""# 五行分析

## 日主信息
- **日主**: {data['day_master']}
- **五行**: {data['day_master_element']}

## 五行分数
| 五行 | 数量 | 百分比 |
|------|------|--------|
| 金 | {data['scores']['金']} | {data['percentages']['金']:.1f}% |
| 木 | {data['scores']['木']} | {data['percentages']['木']:.1f}% |
| 水 | {data['scores']['水']} | {data['percentages']['水']:.1f}% |
| 火 | {data['scores']['火']} | {data['percentages']['火']:.1f}% |
| 土 | {data['scores']['土']} | {data['percentages']['土']:.1f}% |

## 分析结果
- **最旺五行**: {data['strongest']['element']}（{data['strongest']['score']}个）
- **最弱五行**: {data['weakest']['element']}（{data['weakest']['score']}个）
- **缺失五行**: {', '.join(data['missing']) if data['missing'] else '无'}
- **平衡度**: {data['balance']}

## 建议
"""

        # 根据五行情况给出建议
        if data["missing"]:
            md += f"\n命局缺{', '.join(data['missing'])}，建议在生活中补充这些元素。\n"

        if data["balance"] == "五行不平衡":
            md += f"\n五行不够平衡，{data['strongest']['element']}过旺，{data['weakest']['element']}较弱，建议适当调和。\n"

        return md
