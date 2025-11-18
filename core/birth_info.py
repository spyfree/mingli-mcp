"""
生辰信息数据模型
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class BirthInfo:
    """生辰信息数据类"""

    date: str  # YYYY-MM-DD格式
    time_index: int  # 0-12，对应子时到晚子时
    gender: str  # "男" 或 "女"
    calendar: str = "solar"  # "solar" 或 "lunar"
    is_leap_month: bool = False  # 是否闰月（仅农历有效）

    # 真太阳时支持（可选）
    longitude: Optional[float] = None  # 出生地经度（东经为正，西经为负）
    latitude: Optional[float] = None  # 出生地纬度（北纬为正，南纬为负）
    use_solar_time: bool = False  # 是否使用真太阳时修正
    birth_hour: Optional[int] = None  # 出生时刻小时（0-23），用于真太阳时精确计算
    birth_minute: Optional[int] = None  # 出生时刻分钟（0-59），用于真太阳时精确计算

    def __post_init__(self):
        """验证数据有效性"""
        if not 0 <= self.time_index <= 12:
            raise ValueError("时辰序号必须在0-12之间")

        if self.gender not in ["男", "女"]:
            raise ValueError("性别必须是'男'或'女'")

        if self.calendar not in ["solar", "lunar"]:
            raise ValueError("历法类型必须是'solar'或'lunar'")

        # 验证日期格式
        try:
            datetime.strptime(self.date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("日期格式必须是YYYY-MM-DD")

        # 真太阳时验证
        if self.use_solar_time:
            if self.longitude is None:
                raise ValueError("使用真太阳时必须提供经度（longitude）")
            if not -180 <= self.longitude <= 180:
                raise ValueError("经度必须在-180到180之间")

            # 如果提供了纬度，验证范围
            if self.latitude is not None and not -90 <= self.latitude <= 90:
                raise ValueError("纬度必须在-90到90之间")

            # 如果提供了具体时刻，验证范围
            if self.birth_hour is not None and not 0 <= self.birth_hour <= 23:
                raise ValueError("小时必须在0-23之间")
            if self.birth_minute is not None and not 0 <= self.birth_minute <= 59:
                raise ValueError("分钟必须在0-59之间")

            # 如果使用真太阳时，建议提供具体时刻
            if self.birth_hour is None or self.birth_minute is None:
                # 这里只是警告，不抛出异常，因为可以使用time_index的中点时间
                pass

    def to_dict(self) -> dict:
        """转换为字典"""
        data = {
            "date": self.date,
            "time_index": self.time_index,
            "gender": self.gender,
            "calendar": self.calendar,
            "is_leap_month": self.is_leap_month,
        }

        # 添加真太阳时相关字段（如果存在）
        if self.longitude is not None:
            data["longitude"] = self.longitude
        if self.latitude is not None:
            data["latitude"] = self.latitude
        if self.use_solar_time:
            data["use_solar_time"] = self.use_solar_time
        if self.birth_hour is not None:
            data["birth_hour"] = self.birth_hour
        if self.birth_minute is not None:
            data["birth_minute"] = self.birth_minute

        return data

    @classmethod
    def from_dict(cls, data: dict) -> "BirthInfo":
        """从字典创建"""
        return cls(
            date=data["date"],
            time_index=data["time_index"],
            gender=data["gender"],
            calendar=data.get("calendar", "solar"),
            is_leap_month=data.get("is_leap_month", False),
            longitude=data.get("longitude"),
            latitude=data.get("latitude"),
            use_solar_time=data.get("use_solar_time", False),
            birth_hour=data.get("birth_hour"),
            birth_minute=data.get("birth_minute"),
        )

    def get_time_range(self) -> str:
        """获取时辰对应的时间段"""
        time_ranges = [
            "23:00~01:00",  # 0 早子时
            "01:00~03:00",  # 1 丑时
            "03:00~05:00",  # 2 寅时
            "05:00~07:00",  # 3 卯时
            "07:00~09:00",  # 4 辰时
            "09:00~11:00",  # 5 巳时
            "11:00~13:00",  # 6 午时
            "13:00~15:00",  # 7 未时
            "15:00~17:00",  # 8 申时
            "17:00~19:00",  # 9 酉时
            "19:00~21:00",  # 10 戌时
            "21:00~23:00",  # 11 亥时
            "23:00~01:00",  # 12 晚子时
        ]
        return time_ranges[self.time_index]

    def get_time_name(self) -> str:
        """获取时辰名称"""
        time_names = [
            "早子时",
            "丑时",
            "寅时",
            "卯时",
            "辰时",
            "巳时",
            "午时",
            "未时",
            "申时",
            "酉时",
            "戌时",
            "亥时",
            "晚子时",
        ]
        return time_names[self.time_index]

    def get_adjusted_time_index(self) -> int:
        """
        获取真太阳时修正后的时辰序号

        如果use_solar_time=True且提供了经度，则根据真太阳时计算时辰序号；
        否则返回原始的time_index。

        Returns:
            修正后的时辰序号（0-12）

        Examples:
            >>> # 不使用真太阳时
            >>> info = BirthInfo(date="2000-08-16", time_index=6, gender="女")
            >>> info.get_adjusted_time_index()
            6

            >>> # 使用真太阳时（乌鲁木齐，经度87.6°，时差约-129分钟）
            >>> info = BirthInfo(
            ...     date="2000-08-16", time_index=6, gender="女",
            ...     longitude=87.6, use_solar_time=True,
            ...     birth_hour=12, birth_minute=0
            ... )
            >>> info.get_adjusted_time_index()  # 12:00 - 129分钟 ≈ 9:51，仍是巳时(5)
            5
        """
        if not self.use_solar_time or self.longitude is None:
            return self.time_index

        # 延迟导入避免循环依赖
        from utils.solar_time import adjust_time_index_for_solar_time

        # 获取出生时刻
        if self.birth_hour is not None and self.birth_minute is not None:
            hour = self.birth_hour
            minute = self.birth_minute
        else:
            # 如果没有提供具体时刻，使用时辰的中点时间
            hour, minute = self._get_time_index_midpoint()

        # 计算真太阳时修正后的时辰
        adjusted_index, _, _ = adjust_time_index_for_solar_time(hour, minute, self.longitude)

        return adjusted_index

    def _get_time_index_midpoint(self) -> tuple[int, int]:
        """
        获取时辰的中点时间（小时，分钟）

        Returns:
            (小时, 分钟) 元组

        Examples:
            >>> info = BirthInfo(date="2000-08-16", time_index=6, gender="女")
            >>> info._get_time_index_midpoint()
            (12, 0)  # 午时中点
        """
        # 时辰中点映射（小时, 分钟）
        midpoints = [
            (0, 0),  # 0 早子时 (23:00-01:00) -> 00:00
            (2, 0),  # 1 丑时 (01:00-03:00) -> 02:00
            (4, 0),  # 2 寅时 (03:00-05:00) -> 04:00
            (6, 0),  # 3 卯时 (05:00-07:00) -> 06:00
            (8, 0),  # 4 辰时 (07:00-09:00) -> 08:00
            (10, 0),  # 5 巳时 (09:00-11:00) -> 10:00
            (12, 0),  # 6 午时 (11:00-13:00) -> 12:00
            (14, 0),  # 7 未时 (13:00-15:00) -> 14:00
            (16, 0),  # 8 申时 (15:00-17:00) -> 16:00
            (18, 0),  # 9 酉时 (17:00-19:00) -> 18:00
            (20, 0),  # 10 戌时 (19:00-21:00) -> 20:00
            (22, 0),  # 11 亥时 (21:00-23:00) -> 22:00
            (0, 0),  # 12 晚子时 (23:00-01:00) -> 00:00（次日）
        ]
        return midpoints[self.time_index]

    def get_solar_time_info(self) -> Optional[str]:
        """
        获取真太阳时信息（用于日志和调试）

        Returns:
            格式化的真太阳时信息字符串，如果不使用真太阳时则返回None

        Examples:
            >>> info = BirthInfo(
            ...     date="2000-08-16", time_index=6, gender="女",
            ...     longitude=116.4, use_solar_time=True,
            ...     birth_hour=12, birth_minute=0
            ... )
            >>> print(info.get_solar_time_info())
            北京时间: 2000-08-16 12:00
            出生地经度: 116.4°E
            时差: -14分钟
            真太阳时: 2000-08-16 11:46
            修正前时辰: 午时 (序号: 6)
            修正后时辰: 午时 (序号: 6)
        """
        if not self.use_solar_time or self.longitude is None:
            return None

        # 延迟导入
        from utils.solar_time import (
            calculate_solar_time_offset,
            beijing_to_solar_time,
        )

        # 获取出生时刻
        if self.birth_hour is not None and self.birth_minute is not None:
            hour = self.birth_hour
            minute = self.birth_minute
        else:
            hour, minute = self._get_time_index_midpoint()

        # 创建临时datetime
        birth_datetime = datetime.strptime(self.date, "%Y-%m-%d")
        birth_datetime = birth_datetime.replace(hour=hour, minute=minute)

        # 计算真太阳时
        solar_datetime = beijing_to_solar_time(birth_datetime, self.longitude)
        offset = calculate_solar_time_offset(self.longitude)
        adjusted_index = self.get_adjusted_time_index()

        offset_str = f"+{offset}分钟" if offset > 0 else f"{offset}分钟"

        return f"""北京时间: {birth_datetime.strftime('%Y-%m-%d %H:%M')}
出生地经度: {self.longitude}°E
时差: {offset_str}
真太阳时: {solar_datetime.strftime('%Y-%m-%d %H:%M')}
修正前时辰: {self.get_time_name()} (序号: {self.time_index})
修正后时辰: {self._get_time_name_by_index(adjusted_index)} (序号: {adjusted_index})"""

    def _get_time_name_by_index(self, index: int) -> str:
        """根据时辰序号获取时辰名称"""
        time_names = [
            "早子时",
            "丑时",
            "寅时",
            "卯时",
            "辰时",
            "巳时",
            "午时",
            "未时",
            "申时",
            "酉时",
            "戌时",
            "亥时",
            "晚子时",
        ]
        return time_names[index]
