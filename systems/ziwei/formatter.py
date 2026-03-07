"""
紫微斗数结果格式化器

将iztro-py返回的数据格式化为易读的Markdown格式
"""

from datetime import datetime
from typing import Any, Dict, List

from iztro_py.i18n import t


class ZiweiFormatter:
    """紫微斗数格式化器（使用 iztro-py 0.3.0+ 的国际化功能）"""

    # 天干地支映射（用于运势对象，因为 HoroscopeItem 没有 translate 方法）
    HEAVENLY_STEMS = {
        "jiaHeavenly": "甲",
        "yiHeavenly": "乙",
        "bingHeavenly": "丙",
        "dingHeavenly": "丁",
        "wuHeavenly": "戊",
        "jiHeavenly": "己",
        "gengHeavenly": "庚",
        "xinHeavenly": "辛",
        "renHeavenly": "壬",
        "guiHeavenly": "癸",
    }

    EARTHLY_BRANCHES = {
        "ziEarthly": "子",
        "chouEarthly": "丑",
        "yinEarthly": "寅",
        "maoEarthly": "卯",
        "chenEarthly": "辰",
        "siEarthly": "巳",
        "wuEarthly": "午",
        "weiEarthly": "未",
        "shenEarthly": "申",
        "youEarthly": "酉",
        "xuEarthly": "戌",
        "haiEarthly": "亥",
    }

    def format_chart(self, astrolabe) -> Dict[str, Any]:
        """
        格式化星盘数据

        Args:
            astrolabe: iztro-py返回的astrolabe对象

        Returns:
            格式化后的星盘数据字典
        """
        return {
            "system": "紫微斗数",
            "basic_info": {
                "阳历日期": astrolabe.solar_date,
                "农历日期": astrolabe.lunar_date,
                "四柱": astrolabe.chinese_date,
                "时辰": astrolabe.time,
                "时间段": astrolabe.time_range,
                "星座": astrolabe.sign,
                "生肖": astrolabe.zodiac,
                "命宫地支": astrolabe.earthly_branch_of_soul_palace,
                "身宫地支": astrolabe.earthly_branch_of_body_palace,
                "命主": astrolabe.soul,
                "身主": astrolabe.body,
                "五行局": astrolabe.five_elements_class,
            },
            "palaces": self._format_palaces(astrolabe.palaces),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "version": "1.0.0",
            },
        }

    def format_chart_markdown(self, chart_data: Dict[str, Any]) -> str:
        """
        将星盘数据格式化为Markdown

        Args:
            chart_data: format_chart返回的字典

        Returns:
            Markdown格式的字符串
        """
        md = f"# {chart_data['system']}排盘\n\n"

        # 基本信息
        md += "## 基本信息\n\n"
        for key, value in chart_data["basic_info"].items():
            md += f"- **{key}**: {value}\n"

        # 十二宫详情
        md += "\n## 十二宫详情\n\n"
        for palace in chart_data["palaces"]:
            md += self._format_palace_markdown(palace)

        return md

    def format_fortune(
        self, horoscope, query_date: datetime, language: str = "zh-CN"
    ) -> Dict[str, Any]:
        """
        格式化运势数据

        Args:
            horoscope: iztro-py返回的horoscope对象
            query_date: 查询日期

        Returns:
            格式化后的运势数据字典
        """
        result = {
            "query_date": query_date.strftime("%Y-%m-%d"),
            "solar_date": horoscope.solar_date,
            "lunar_date": horoscope.lunar_date,
        }

        # 大限
        if hasattr(horoscope, "decadal"):
            result["decadal"] = self._format_limit(horoscope.decadal, "大限", language)

        # 流年
        if hasattr(horoscope, "yearly"):
            result["yearly"] = self._format_limit(horoscope.yearly, "流年", language)

        # 流月
        if hasattr(horoscope, "monthly"):
            result["monthly"] = self._format_limit(horoscope.monthly, "流月", language)

        # 流日
        if hasattr(horoscope, "daily"):
            result["daily"] = self._format_limit(horoscope.daily, "流日", language)

        # 流时
        if hasattr(horoscope, "hourly"):
            result["hourly"] = self._format_limit(horoscope.hourly, "流时", language)

        return result

    def format_fortune_markdown(self, fortune_data: Dict[str, Any]) -> str:
        """
        将运势数据格式化为Markdown

        Args:
            fortune_data: format_fortune返回的字典

        Returns:
            Markdown格式的字符串
        """
        md = "# 紫微斗数运势\n\n"
        md += f"**查询日期**: {fortune_data['query_date']}\n\n"
        md += f"**阳历**: {fortune_data['solar_date']}\n\n"
        md += f"**农历**: {fortune_data['lunar_date']}\n\n"

        # 各运限
        for key in ["decadal", "yearly", "monthly", "daily", "hourly"]:
            if key in fortune_data:
                limit_data = fortune_data[key]
                md += f"## {limit_data['name']}\n\n"
                md += (
                    f"- **天干地支**: {limit_data['heavenly_stem']}{limit_data['earthly_branch']}\n"
                )
                md += f"- **宫位顺序**: {' → '.join(limit_data['palace_names'])}\n"

                if limit_data.get("mutagen"):
                    md += f"- **四化**: {', '.join(limit_data['mutagen'])}\n"

                if limit_data.get("age"):
                    md += f"- **年龄范围**: {limit_data['age']}\n"

                md += "\n"

        return md

    def format_palace_analysis(
        self, palace: Dict[str, Any], basic_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        格式化宫位分析

        Args:
            palace: 宫位数据
            basic_info: 基本信息

        Returns:
            格式化后的宫位分析
        """
        return {
            "palace_name": palace["name"],
            "is_body_palace": palace.get("is_body_palace", False),
            "is_original_palace": palace.get("is_original_palace", False),
            "heavenly_stem": palace["heavenly_stem"],
            "earthly_branch": palace["earthly_branch"],
            "major_stars": palace.get("major_stars", []),
            "minor_stars": palace.get("minor_stars", []),
            "adjective_stars": palace.get("adjective_stars", []),
            "changsheng12": palace.get("changsheng12", ""),
            "boshi12": palace.get("boshi12", ""),
            "stage": palace.get("stage", {}),
            "basic_info": basic_info,
        }

    def format_palace_analysis_markdown(self, analysis: Dict[str, Any]) -> str:
        """
        将宫位分析格式化为Markdown

        Args:
            analysis: format_palace_analysis返回的字典

        Returns:
            Markdown格式的字符串
        """
        palace_name = analysis["palace_name"]
        markers = []
        if analysis["is_body_palace"]:
            markers.append("⭐身宫")
        if analysis["is_original_palace"]:
            markers.append("🏠来因宫")

        title = f"# {palace_name}宫位分析"
        if markers:
            title += f" {' '.join(markers)}"

        md = title + "\n\n"

        # 宫位基本信息
        md += "## 宫位信息\n\n"
        md += f"- **天干地支**: {analysis['heavenly_stem']}{analysis['earthly_branch']}\n"

        if analysis.get("stage"):
            stage = analysis["stage"]
            if isinstance(stage, dict) and "range" in stage:
                md += f"- **大限**: {stage['range'][0]}-{stage['range'][1]}岁\n"

        if analysis.get("changsheng12"):
            md += f"- **长生十二神**: {analysis['changsheng12']}\n"

        if analysis.get("boshi12"):
            md += f"- **博士十二神**: {analysis['boshi12']}\n"

        # 星曜信息
        md += "\n## 星曜配置\n\n"

        if analysis.get("major_stars"):
            md += "### 主星\n\n"
            for star in analysis["major_stars"]:
                brightness = f"({star.get('brightness', '')})" if star.get("brightness") else ""
                md += f"- **{star['name']}** {brightness}\n"
            md += "\n"

        if analysis.get("minor_stars"):
            md += "### 辅星\n\n"
            for star in analysis["minor_stars"]:
                brightness = f"({star.get('brightness', '')})" if star.get("brightness") else ""
                md += f"- {star['name']} {brightness}\n"
            md += "\n"

        if analysis.get("adjective_stars"):
            md += "### 杂耀\n\n"
            star_names = [star["name"] for star in analysis["adjective_stars"]]
            md += f"{', '.join(star_names)}\n\n"

        return md

    def _format_palaces(self, palaces) -> List[Dict[str, Any]]:
        """格式化十二宫数据（使用 iztro-py 0.3.0 的翻译方法）"""
        result = []
        for palace in palaces:
            # 使用 translate_name() 获取中文宫位名（iztro-py 0.3.0+）
            chinese_name = palace.translate_name()

            # 使用翻译方法获取中文天干地支
            heavenly_stem = palace.translate_heavenly_stem()
            earthly_branch = palace.translate_earthly_branch()

            result.append(
                {
                    "name": chinese_name,
                    "is_body_palace": palace.is_body_palace,
                    "is_original_palace": palace.is_original_palace,
                    "heavenly_stem": heavenly_stem,
                    "earthly_branch": earthly_branch,
                    "major_stars": [self._format_star(s) for s in palace.major_stars],
                    "minor_stars": [self._format_star(s) for s in palace.minor_stars],
                    "adjective_stars": [self._format_star(s) for s in palace.adjective_stars],
                    "changsheng12": palace.changsheng12,
                    "boshi12": palace.boshi12,
                    "stage": (
                        self._format_stage(palace.decadal) if hasattr(palace, "decadal") else {}
                    ),
                }
            )
        return result

    def _format_star(self, star) -> Dict[str, str]:
        """格式化星曜数据（使用 iztro-py 0.3.0 的翻译方法）"""
        # 使用 translate_name() 获取中文星曜名
        star_name = star.translate_name() if hasattr(star, "translate_name") else star.name

        # 使用 translate_brightness() 获取中文亮度描述
        brightness = ""
        if hasattr(star, "translate_brightness") and star.brightness:
            try:
                brightness = star.translate_brightness()
            except Exception:
                brightness = getattr(star, "brightness", "")
        else:
            brightness = getattr(star, "brightness", "")

        return {
            "name": star_name,
            "type": star.type,
            "brightness": brightness,
            "scope": getattr(star, "scope", "origin"),
        }

    def _format_stage(self, stage) -> Dict[str, Any]:
        """格式化大限数据（使用 iztro-py 0.3.0 的翻译方法）"""
        if hasattr(stage, "range"):
            # 使用翻译方法获取中文天干
            heavenly_stem = (
                stage.translate_heavenly_stem()
                if hasattr(stage, "translate_heavenly_stem")
                else stage.heavenly_stem
            )
            return {
                "range": list(stage.range),
                "heavenly_stem": heavenly_stem,
            }
        return {}

    def _translate_palace_name(self, palace_name: str, language: str) -> str:
        """将运限中的内部宫位 ID 翻译为用户可读文本。"""
        if isinstance(palace_name, str) and palace_name.endswith("Palace"):
            return t(f"palaces.{palace_name}", language)
        return palace_name

    def _translate_star_name(self, star_name: str, language: str) -> str:
        """将内部星曜 ID 翻译为用户可读文本。"""
        if not isinstance(star_name, str):
            return star_name
        if star_name.endswith("Maj"):
            return t(f"stars.major.{star_name}", language)
        if star_name.endswith("Min"):
            return t(f"stars.minor.{star_name}", language)
        return star_name

    def _format_limit(self, limit, name: str, language: str) -> Dict[str, Any]:
        """格式化运限数据（运势对象没有 translate 方法，使用映射表）"""
        # HoroscopeItem 没有 translate 方法，使用映射表翻译
        heavenly_stem = self.HEAVENLY_STEMS.get(limit.heavenly_stem, limit.heavenly_stem)
        earthly_branch = self.EARTHLY_BRANCHES.get(limit.earthly_branch, limit.earthly_branch)

        result = {
            "name": name,
            "index": limit.index,
            "heavenly_stem": heavenly_stem,
            "earthly_branch": earthly_branch,
            "palace_names": [
                self._translate_palace_name(palace_name, language)
                for palace_name in limit.palace_names
            ],
        }

        if hasattr(limit, "mutagen"):
            result["mutagen"] = [
                self._translate_star_name(star_name, language) for star_name in limit.mutagen
            ]

        if hasattr(limit, "age"):
            age = limit.age
            if hasattr(age, "nominal_age"):
                result["age"] = f"{age.nominal_age}岁"

        return result

    def _format_palace_markdown(self, palace: Dict[str, Any]) -> str:
        """格式化单个宫位为Markdown"""
        markers = []
        if palace.get("is_body_palace"):
            markers.append("⭐")
        if palace.get("is_original_palace"):
            markers.append("🏠")

        marker_str = "".join(markers) + " " if markers else ""

        md = f"### {marker_str}{palace['name']}宫 ({palace['heavenly_stem']}{palace['earthly_branch']})\n\n"

        if palace.get("major_stars"):
            stars = []
            for star in palace["major_stars"]:
                name = star["name"]
                brightness = f"({star['brightness']})" if star.get("brightness") else ""
                stars.append(f"{name}{brightness}")
            md += f"- **主星**: {', '.join(stars)}\n"

        if palace.get("minor_stars"):
            stars = [s["name"] for s in palace["minor_stars"]]
            md += f"- **辅星**: {', '.join(stars)}\n"

        if palace.get("adjective_stars"):
            stars = [s["name"] for s in palace["adjective_stars"]]
            md += f"- **杂耀**: {', '.join(stars)}\n"

        if palace.get("stage"):
            stage = palace["stage"]
            if isinstance(stage, dict) and stage.get("range"):
                md += f"- **大限**: {stage['range'][0]}-{stage['range'][1]}岁\n"

        md += "\n"
        return md
