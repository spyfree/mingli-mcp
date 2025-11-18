"""
命理系统抽象基类

定义统一的接口，支持不同命理系统（紫微、八字、占星等）
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

from .exceptions import ValidationError


class BaseFortuneSystem(ABC):
    """命理系统抽象基类"""

    @abstractmethod
    def get_system_name(self) -> str:
        """
        返回系统名称

        Returns:
            系统名称，如 "紫微斗数"、"八字"、"西方占星"
        """
        pass

    @abstractmethod
    def get_system_version(self) -> str:
        """
        返回系统版本

        Returns:
            版本号字符串
        """
        pass

    @abstractmethod
    def get_chart(self, birth_info: Dict[str, Any], language: str = "zh-CN") -> Dict[str, Any]:
        """
        获取排盘信息

        Args:
            birth_info: 生辰信息字典，包含以下字段：
                - date: 日期 (str格式 YYYY-MM-DD 或 datetime对象)
                - time_index: 时辰序号 (int, 0-12)
                - gender: 性别 (str, "男"/"女")
                - calendar: 历法 (str, "solar"/"lunar", 默认"solar")
                - is_leap_month: 是否闰月 (bool, 默认False, 仅农历有效)
            language: 输出语言 (str, 默认"zh-CN")
                支持: zh-CN, zh-TW, en-US, ja-JP, ko-KR, vi-VN

        Returns:
            排盘详细信息字典，包含：
                - system: 系统名称
                - basic_info: 基本信息（日期、时辰、星座等）
                - palaces/houses: 宫位信息
                - stars: 星曜信息
                - elements: 五行信息
                - ... (各系统特有数据)

        Raises:
            ValueError: 参数格式错误
            RuntimeError: 排盘计算错误
        """
        pass

    @abstractmethod
    def get_fortune(
        self,
        birth_info: Dict[str, Any],
        query_date: Optional[datetime] = None,
        language: str = "zh-CN",
    ) -> Dict[str, Any]:
        """
        获取运势信息

        Args:
            birth_info: 生辰信息字典（同get_chart）
            query_date: 查询日期，默认为当前时间
            language: 输出语言 (str, 默认"zh-CN")
                支持: zh-CN, zh-TW, en-US, ja-JP, ko-KR, vi-VN

        Returns:
            运势信息字典，可能包含：
                - decadal: 大限（紫微）
                - yearly: 流年
                - monthly: 流月
                - daily: 流日
                - ... (各系统特有运势)

        Raises:
            ValueError: 参数错误
            RuntimeError: 运势计算错误
        """
        pass

    @abstractmethod
    def analyze_palace(
        self, birth_info: Dict[str, Any], palace_name: str, language: str = "zh-CN"
    ) -> Dict[str, Any]:
        """
        分析特定宫位的详细信息

        Args:
            birth_info: 生辰信息字典
            palace_name: 宫位名称（各系统定义不同）
            language: 输出语言 (str, 默认"zh-CN")
                支持: zh-CN, zh-TW, en-US, ja-JP, ko-KR, vi-VN

        Returns:
            宫位详细分析字典，包含：
                - palace_name: 宫位名称
                - basic_info: 基本信息
                - stars: 该宫位的星曜
                - interpretation: 解读信息（可选）

        Raises:
            ValueError: 宫位名称无效
        """
        pass

    def validate_birth_info(self, birth_info: Dict[str, Any]) -> None:
        """
        验证生辰信息的有效性

        Args:
            birth_info: 生辰信息字典

        Raises:
            ValidationError: 参数无效或缺失
            DateRangeError: 日期超出支持范围
        """
        # 延迟导入避免循环依赖
        from utils.validators import validate_date_range

        required_fields = ["date", "time_index", "gender"]
        for field in required_fields:
            if field not in birth_info:
                raise ValidationError(f"缺少必需字段: {field}")

        # 验证日期格式和范围
        validate_date_range(birth_info["date"])

        # 验证时辰
        if not 0 <= birth_info["time_index"] <= 12:
            raise ValidationError("时辰序号必须在0-12之间")

        # 验证性别
        if birth_info["gender"] not in ["男", "女"]:
            raise ValidationError("性别必须是'男'或'女'")

    def validate_language(self, language: str) -> None:
        """
        验证语言是否支持

        Args:
            language: 语言代码

        Raises:
            LanguageNotSupportedError: 语言不支持
        """
        # 延迟导入避免循环依赖
        from utils.validators import validate_language as _validate_language

        _validate_language(language)

    def get_supported_palaces(self) -> list:
        """
        返回该系统支持的宫位列表

        Returns:
            宫位名称列表
        """
        return []

    def get_capabilities(self) -> Dict[str, bool]:
        """
        返回系统支持的功能

        Returns:
            功能字典，例如：
            {
                'chart': True,
                'fortune': True,
                'palace_analysis': True,
                'compatibility': False,
                ...
            }
        """
        return {
            "chart": True,
            "fortune": False,
            "palace_analysis": False,
            "compatibility": False,
        }

    def apply_solar_time_correction(self, birth_info: Dict[str, Any]) -> int:
        """
        应用真太阳时修正，返回修正后的时辰序号

        如果birth_info中指定了use_solar_time=True且提供了经度，
        则计算真太阳时修正后的时辰序号；否则返回原始time_index。

        Args:
            birth_info: 生辰信息字典

        Returns:
            修正后的时辰序号 (0-12)

        Examples:
            >>> birth_info = {
            ...     "date": "2000-08-16",
            ...     "time_index": 6,
            ...     "gender": "女",
            ...     "use_solar_time": True,
            ...     "longitude": 87.6,  # 乌鲁木齐
            ...     "birth_hour": 12,
            ...     "birth_minute": 0
            ... }
            >>> system.apply_solar_time_correction(birth_info)
            5  # 真太阳时修正后变为巳时
        """
        # 检查是否启用真太阳时
        if not birth_info.get("use_solar_time", False):
            return birth_info["time_index"]

        # 检查是否提供了经度
        longitude = birth_info.get("longitude")
        if longitude is None:
            return birth_info["time_index"]

        # 导入真太阳时计算函数
        from utils.solar_time import adjust_time_index_for_solar_time

        # 获取出生时刻
        birth_hour = birth_info.get("birth_hour")
        birth_minute = birth_info.get("birth_minute")

        # 如果没有提供具体时刻，使用时辰的中点时间
        if birth_hour is None or birth_minute is None:
            birth_hour, birth_minute = self._get_time_index_midpoint(
                birth_info["time_index"]
            )

        # 计算真太阳时修正后的时辰
        adjusted_index, _, _ = adjust_time_index_for_solar_time(
            birth_hour, birth_minute, longitude
        )

        return adjusted_index

    def _get_time_index_midpoint(self, time_index: int) -> tuple[int, int]:
        """
        获取时辰的中点时间（小时，分钟）

        Args:
            time_index: 时辰序号 (0-12)

        Returns:
            (小时, 分钟) 元组
        """
        midpoints = [
            (0, 0),   # 0 早子时
            (2, 0),   # 1 丑时
            (4, 0),   # 2 寅时
            (6, 0),   # 3 卯时
            (8, 0),   # 4 辰时
            (10, 0),  # 5 巳时
            (12, 0),  # 6 午时
            (14, 0),  # 7 未时
            (16, 0),  # 8 申时
            (18, 0),  # 9 酉时
            (20, 0),  # 10 戌时
            (22, 0),  # 11 亥时
            (0, 0),   # 12 晚子时
        ]
        return midpoints[time_index]
