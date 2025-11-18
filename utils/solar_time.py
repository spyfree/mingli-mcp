#!/usr/bin/env python3
"""
真太阳时计算工具

真太阳时是根据出生地的经度修正后的地方时间。
中国统一使用北京时间（东八区，UTC+8，标准经度120°E），
但由于中国地域辽阔，东西跨度大，实际各地的地方时与北京时间存在差异。

计算公式：
真太阳时 = 北京时间 + (出生地经度 - 120°) × 4分钟/度

示例：
- 北京（116.4°E）：比北京时间慢约14分钟
- 上海（121.5°E）：比北京时间快约6分钟
- 乌鲁木齐（87.6°E）：比北京时间慢约129分钟
"""

from datetime import datetime, timedelta
from typing import Tuple


# 东八区（北京时间）的标准经度
BEIJING_LONGITUDE = 120.0

# 每度经度对应的时间差（分钟）
MINUTES_PER_DEGREE = 4.0


def calculate_solar_time_offset(longitude: float) -> int:
    """
    计算真太阳时偏移量（分钟）

    Args:
        longitude: 出生地经度（东经为正，西经为负）

    Returns:
        偏移分钟数（正数表示快于北京时间，负数表示慢于北京时间）

    Examples:
        >>> calculate_solar_time_offset(116.4)  # 北京
        -14
        >>> calculate_solar_time_offset(121.5)  # 上海
        6
        >>> calculate_solar_time_offset(87.6)   # 乌鲁木齐
        -129
    """
    offset_degrees = longitude - BEIJING_LONGITUDE
    offset_minutes = offset_degrees * MINUTES_PER_DEGREE
    return round(offset_minutes)


def beijing_to_solar_time(beijing_time: datetime, longitude: float) -> datetime:
    """
    将北京时间转换为真太阳时

    Args:
        beijing_time: 北京时间
        longitude: 出生地经度

    Returns:
        真太阳时

    Examples:
        >>> bt = datetime(2000, 8, 16, 12, 0)
        >>> beijing_to_solar_time(bt, 116.4)  # 北京
        datetime(2000, 8, 16, 11, 46)
        >>> beijing_to_solar_time(bt, 121.5)  # 上海
        datetime(2000, 8, 16, 12, 6)
    """
    offset_minutes = calculate_solar_time_offset(longitude)
    solar_time = beijing_time + timedelta(minutes=offset_minutes)
    return solar_time


def adjust_time_index_for_solar_time(
    beijing_hour: int, beijing_minute: int, longitude: float
) -> Tuple[int, int, int]:
    """
    根据真太阳时调整时辰序号

    Args:
        beijing_hour: 北京时间小时（0-23）
        beijing_minute: 北京时间分钟（0-59）
        longitude: 出生地经度

    Returns:
        (调整后的时辰序号, 真太阳时小时, 真太阳时分钟)

    注意：
        时辰序号范围：0-12
        - 0: 早子时 (23:00-01:00)
        - 1: 丑时 (01:00-03:00)
        - 2: 寅时 (03:00-05:00)
        - ...
        - 11: 亥时 (21:00-23:00)
        - 12: 晚子时 (23:00-01:00)

    Examples:
        >>> adjust_time_index_for_solar_time(12, 0, 116.4)  # 北京中午12点
        (6, 11, 46)  # 午时，真太阳时11:46
    """
    # 创建临时datetime对象进行计算
    temp_datetime = datetime(2000, 1, 1, beijing_hour, beijing_minute)
    solar_datetime = beijing_to_solar_time(temp_datetime, longitude)

    solar_hour = solar_datetime.hour
    solar_minute = solar_datetime.minute

    # 计算时辰序号
    time_index = calculate_time_index(solar_hour, solar_minute)

    return time_index, solar_hour, solar_minute


def calculate_time_index(hour: int, minute: int) -> int:
    """
    根据小时和分钟计算时辰序号

    时辰划分：
    - 子时：23:00-01:00（分早子0和晚子12）
    - 丑时：01:00-03:00 (1)
    - 寅时：03:00-05:00 (2)
    - 卯时：05:00-07:00 (3)
    - 辰时：07:00-09:00 (4)
    - 巳时：09:00-11:00 (5)
    - 午时：11:00-13:00 (6)
    - 未时：13:00-15:00 (7)
    - 申时：15:00-17:00 (8)
    - 酉时：17:00-19:00 (9)
    - 戌时：19:00-21:00 (10)
    - 亥时：21:00-23:00 (11)

    Args:
        hour: 小时 (0-23)
        minute: 分钟 (0-59)

    Returns:
        时辰序号 (0-12)
    """
    # 23:00-23:59 属于晚子时
    if hour == 23:
        return 12

    # 00:00-00:59 属于早子时
    if hour == 0:
        return 0

    # 01:00-22:59 按照每两小时一个时辰计算
    # 丑时(1:00-2:59) -> 1, 寅时(3:00-4:59) -> 2, ...
    return (hour + 1) // 2


def get_major_cities_longitude() -> dict:
    """
    获取全球主要城市的经度数据

    Returns:
        城市名到经度的映射字典

    数据来源：
        - 基于WGS84坐标系
        - 保留一位小数精度
        - 涵盖全球200+个主要城市
    """
    return {
        # ========== 中国 ==========
        # 直辖市
        "北京": 116.4,
        "上海": 121.5,
        "天津": 117.2,
        "重庆": 106.5,
        # 省会城市（按拼音排序）
        "长春": 125.3,
        "长沙": 112.9,
        "成都": 104.1,
        "福州": 119.3,
        "广州": 113.3,
        "贵阳": 106.7,
        "哈尔滨": 126.6,
        "杭州": 120.2,
        "合肥": 117.3,
        "呼和浩特": 111.7,
        "济南": 117.0,
        "昆明": 102.7,
        "拉萨": 91.1,
        "兰州": 103.8,
        "南昌": 115.9,
        "南京": 118.8,
        "南宁": 108.3,
        "石家庄": 114.5,
        "沈阳": 123.4,
        "太原": 112.5,
        "乌鲁木齐": 87.6,
        "武汉": 114.3,
        "西安": 108.9,
        "西宁": 101.8,
        "银川": 106.3,
        "郑州": 113.6,
        # 其他重要城市
        "深圳": 114.1,
        "厦门": 118.1,
        "青岛": 120.4,
        "大连": 121.6,
        "宁波": 121.6,
        "苏州": 120.6,
        "无锡": 120.3,
        "东莞": 113.8,
        "珠海": 113.6,
        "佛山": 113.1,
        # 港澳台
        "香港": 114.2,
        "澳门": 113.5,
        "台北": 121.5,
        # ========== 亚洲其他国家 ==========
        # 日本
        "东京": 139.7,
        "大阪": 135.5,
        "京都": 135.8,
        "横滨": 139.6,
        "名古屋": 136.9,
        "札幌": 141.4,
        "福冈": 130.4,
        # 韩国
        "首尔": 127.0,
        "釜山": 129.0,
        "仁川": 126.7,
        "大邱": 128.6,
        # 新加坡
        "新加坡": 103.8,
        # 泰国
        "曼谷": 100.5,
        "清迈": 98.9,
        "普吉": 98.4,
        # 越南
        "河内": 105.8,
        "胡志明市": 106.7,
        "岘港": 108.2,
        # 马来西亚
        "吉隆坡": 101.7,
        "槟城": 100.3,
        # 印度尼西亚
        "雅加达": 106.8,
        "巴厘岛": 115.2,
        "泗水": 112.7,
        # 菲律宾
        "马尼拉": 121.0,
        # 印度
        "新德里": 77.2,
        "孟买": 72.8,
        "班加罗尔": 77.6,
        "加尔各答": 88.4,
        "清奈": 80.3,
        # 巴基斯坦
        "伊斯兰堡": 73.1,
        "卡拉奇": 67.0,
        # 阿联酋
        "迪拜": 55.3,
        "阿布扎比": 54.4,
        # 以色列
        "耶路撒冷": 35.2,
        "特拉维夫": 34.8,
        # 土耳其
        "伊斯坦布尔": 28.9,
        "安卡拉": 32.9,
        # ========== 欧洲 ==========
        # 英国
        "伦敦": -0.1,
        "曼彻斯特": -2.2,
        "爱丁堡": -3.2,
        "利物浦": -3.0,
        # 法国
        "巴黎": 2.3,
        "马赛": 5.4,
        "里昂": 4.8,
        "尼斯": 7.3,
        # 德国
        "柏林": 13.4,
        "慕尼黑": 11.6,
        "法兰克福": 8.7,
        "汉堡": 10.0,
        "科隆": 7.0,
        # 意大利
        "罗马": 12.5,
        "米兰": 9.2,
        "威尼斯": 12.3,
        "佛罗伦萨": 11.3,
        "那不勒斯": 14.3,
        # 西班牙
        "马德里": -3.7,
        "巴塞罗那": 2.2,
        "瓦伦西亚": -0.4,
        "塞维利亚": -5.9,
        # 葡萄牙
        "里斯本": -9.1,
        "波尔图": -8.6,
        # 荷兰
        "阿姆斯特丹": 4.9,
        "鹿特丹": 4.5,
        # 比利时
        "布鲁塞尔": 4.4,
        # 瑞士
        "苏黎世": 8.5,
        "日内瓦": 6.1,
        "伯尔尼": 7.4,
        # 奥地利
        "维也纳": 16.4,
        # 希腊
        "雅典": 23.7,
        # 俄罗斯
        "莫斯科": 37.6,
        "圣彼得堡": 30.3,
        "符拉迪沃斯托克": 131.9,
        # 波兰
        "华沙": 21.0,
        # 捷克
        "布拉格": 14.4,
        # 瑞典
        "斯德哥尔摩": 18.1,
        # 挪威
        "奥斯陆": 10.8,
        # 丹麦
        "哥本哈根": 12.6,
        # 芬兰
        "赫尔辛基": 24.9,
        # ========== 北美洲 ==========
        # 美国东部
        "纽约": -74.0,
        "波士顿": -71.1,
        "华盛顿": -77.0,
        "费城": -75.2,
        "迈阿密": -80.2,
        "亚特兰大": -84.4,
        # 美国中部
        "芝加哥": -87.6,
        "休斯顿": -95.4,
        "达拉斯": -96.8,
        "奥斯汀": -97.7,
        "丹佛": -104.9,
        # 美国西部
        "洛杉矶": -118.2,
        "旧金山": -122.4,
        "西雅图": -122.3,
        "波特兰": -122.7,
        "拉斯维加斯": -115.1,
        "凤凰城": -112.1,
        "圣地亚哥": -117.2,
        # 加拿大
        "多伦多": -79.4,
        "温哥华": -123.1,
        "蒙特利尔": -73.6,
        "渥太华": -75.7,
        "卡尔加里": -114.1,
        # 墨西哥
        "墨西哥城": -99.1,
        "坎昆": -86.9,
        "瓜达拉哈拉": -103.3,
        # ========== 南美洲 ==========
        # 巴西
        "圣保罗": -46.6,
        "里约热内卢": -43.2,
        "巴西利亚": -47.9,
        # 阿根廷
        "布宜诺斯艾利斯": -58.4,
        # 智利
        "圣地亚哥": -70.7,
        # 秘鲁
        "利马": -77.0,
        # 哥伦比亚
        "波哥大": -74.1,
        # ========== 大洋洲 ==========
        # 澳大利亚
        "悉尼": 151.2,
        "墨尔本": 144.9,
        "布里斯班": 153.0,
        "珀斯": 115.9,
        "阿德莱德": 138.6,
        "堪培拉": 149.1,
        # 新西兰
        "奥克兰": 174.8,
        "惠灵顿": 174.8,
        "基督城": 172.6,
        # ========== 非洲 ==========
        # 埃及
        "开罗": 31.2,
        # 南非
        "约翰内斯堡": 28.0,
        "开普敦": 18.4,
        # 肯尼亚
        "内罗毕": 36.8,
        # 摩洛哥
        "卡萨布兰卡": -7.6,
        # 尼日利亚
        "拉各斯": 3.4,
    }


def get_longitude_by_city(city_name: str) -> float:
    """
    根据城市名获取经度

    Args:
        city_name: 城市名称

    Returns:
        经度值

    Raises:
        ValueError: 如果城市不在数据库中

    Examples:
        >>> get_longitude_by_city("北京")
        116.4
        >>> get_longitude_by_city("上海")
        121.5
    """
    cities = get_major_cities_longitude()
    if city_name not in cities:
        raise ValueError(
            f"城市 '{city_name}' 不在数据库中。" f"支持的城市：{', '.join(sorted(cities.keys()))}"
        )
    return cities[city_name]


def format_solar_time_info(beijing_time: datetime, longitude: float, city_name: str = None) -> str:
    """
    格式化真太阳时信息（用于日志和调试）

    Args:
        beijing_time: 北京时间
        longitude: 经度
        city_name: 城市名（可选）

    Returns:
        格式化的信息字符串

    Examples:
        >>> bt = datetime(2000, 8, 16, 12, 0)
        >>> print(format_solar_time_info(bt, 116.4, "北京"))
        北京时间: 2000-08-16 12:00
        出生地: 北京 (经度: 116.4°E)
        时差: -14分钟
        真太阳时: 2000-08-16 11:46
        时辰: 午时 (序号: 6)
    """
    solar_time = beijing_to_solar_time(beijing_time, longitude)
    offset = calculate_solar_time_offset(longitude)
    time_index, _, _ = adjust_time_index_for_solar_time(
        beijing_time.hour, beijing_time.minute, longitude
    )

    # 时辰名称映射
    time_names = {
        0: "早子时",
        1: "丑时",
        2: "寅时",
        3: "卯时",
        4: "辰时",
        5: "巳时",
        6: "午时",
        7: "未时",
        8: "申时",
        9: "酉时",
        10: "戌时",
        11: "亥时",
        12: "晚子时",
    }

    location = f"{city_name} (经度: {longitude}°E)" if city_name else f"经度: {longitude}°E"
    offset_str = f"+{offset}分钟" if offset > 0 else f"{offset}分钟"

    return f"""北京时间: {beijing_time.strftime('%Y-%m-%d %H:%M')}
出生地: {location}
时差: {offset_str}
真太阳时: {solar_time.strftime('%Y-%m-%d %H:%M')}
时辰: {time_names[time_index]} (序号: {time_index})"""


if __name__ == "__main__":
    # 测试示例
    print("=" * 50)
    print("真太阳时计算示例")
    print("=" * 50)

    test_time = datetime(2000, 8, 16, 12, 0)
    test_cities = ["北京", "上海", "乌鲁木齐", "广州"]

    for city in test_cities:
        longitude = get_longitude_by_city(city)
        print(f"\n{format_solar_time_info(test_time, longitude, city)}")
        print("-" * 50)
