#!/usr/bin/env python3
"""
真太阳时计算测试
"""

import pytest
from datetime import datetime

from utils.solar_time import (
    calculate_solar_time_offset,
    beijing_to_solar_time,
    adjust_time_index_for_solar_time,
    calculate_time_index,
    get_longitude_by_city,
    get_major_cities_longitude,
)
from core.birth_info import BirthInfo


class TestSolarTimeOffset:
    """真太阳时偏移量计算测试"""

    def test_beijing_offset(self):
        """测试北京的时差"""
        offset = calculate_solar_time_offset(116.4)
        assert offset == -14  # 比北京时间慢14分钟

    def test_shanghai_offset(self):
        """测试上海的时差"""
        offset = calculate_solar_time_offset(121.5)
        assert offset == 6  # 比北京时间快6分钟

    def test_urumqi_offset(self):
        """测试乌鲁木齐的时差"""
        offset = calculate_solar_time_offset(87.6)
        assert offset == -130  # 比北京时间慢约130分钟

    def test_guangzhou_offset(self):
        """测试广州的时差"""
        offset = calculate_solar_time_offset(113.3)
        assert offset == -27  # 比北京时间慢27分钟

    def test_standard_longitude(self):
        """测试标准经度（120°）的时差"""
        offset = calculate_solar_time_offset(120.0)
        assert offset == 0  # 无时差


class TestBeijingToSolarTime:
    """北京时间转真太阳时测试"""

    def test_beijing_conversion(self):
        """测试北京时间转换"""
        bt = datetime(2000, 8, 16, 12, 0)
        st = beijing_to_solar_time(bt, 116.4)
        assert st.hour == 11
        assert st.minute == 46

    def test_shanghai_conversion(self):
        """测试上海时间转换"""
        bt = datetime(2000, 8, 16, 12, 0)
        st = beijing_to_solar_time(bt, 121.5)
        assert st.hour == 12
        assert st.minute == 6

    def test_urumqi_conversion(self):
        """测试乌鲁木齐时间转换"""
        bt = datetime(2000, 8, 16, 12, 0)
        st = beijing_to_solar_time(bt, 87.6)
        assert st.hour == 9
        assert st.minute == 50


class TestTimeIndexCalculation:
    """时辰序号计算测试"""

    def test_zi_shi_early(self):
        """测试早子时"""
        assert calculate_time_index(0, 0) == 0
        assert calculate_time_index(0, 59) == 0

    def test_zi_shi_late(self):
        """测试晚子时"""
        assert calculate_time_index(23, 0) == 12
        assert calculate_time_index(23, 59) == 12

    def test_chou_shi(self):
        """测试丑时"""
        assert calculate_time_index(1, 0) == 1
        assert calculate_time_index(2, 59) == 1

    def test_wu_shi(self):
        """测试午时"""
        assert calculate_time_index(11, 0) == 6
        assert calculate_time_index(12, 59) == 6

    def test_you_shi(self):
        """测试酉时"""
        assert calculate_time_index(17, 0) == 9
        assert calculate_time_index(18, 59) == 9


class TestAdjustTimeIndexForSolarTime:
    """真太阳时时辰修正测试"""

    def test_beijing_no_change(self):
        """测试北京时辰不变"""
        # 北京12:00，午时，真太阳时11:46仍是午时
        index, hour, minute = adjust_time_index_for_solar_time(12, 0, 116.4)
        assert index == 6  # 午时
        assert hour == 11
        assert minute == 46

    def test_urumqi_time_change(self):
        """测试乌鲁木齐时辰改变"""
        # 乌鲁木齐12:00，原本午时，真太阳时9:50变为巳时
        index, hour, minute = adjust_time_index_for_solar_time(12, 0, 87.6)
        assert index == 5  # 巳时
        assert hour == 9
        assert minute == 50

    def test_boundary_case_1(self):
        """测试时辰边界情况1"""
        # 北京11:00，原本午时，真太阳时10:46仍是巳时
        index, hour, minute = adjust_time_index_for_solar_time(11, 0, 116.4)
        assert index == 5  # 巳时（10:46）

    def test_boundary_case_2(self):
        """测试时辰边界情况2"""
        # 上海11:00，原本午时，真太阳时11:06仍是午时
        index, hour, minute = adjust_time_index_for_solar_time(11, 0, 121.5)
        assert index == 6  # 午时（11:06）


class TestCityLongitude:
    """城市经度查询测试"""

    def test_major_cities_exist(self):
        """测试主要城市都存在"""
        cities = get_major_cities_longitude()
        assert "北京" in cities
        assert "上海" in cities
        assert "广州" in cities
        assert "深圳" in cities

    def test_get_longitude_beijing(self):
        """测试获取北京经度"""
        longitude = get_longitude_by_city("北京")
        assert longitude == 116.4

    def test_get_longitude_urumqi(self):
        """测试获取乌鲁木齐经度"""
        longitude = get_longitude_by_city("乌鲁木齐")
        assert longitude == 87.6

    def test_invalid_city(self):
        """测试无效城市名"""
        with pytest.raises(ValueError) as exc_info:
            get_longitude_by_city("不存在的城市")
        assert "不在数据库中" in str(exc_info.value)


class TestBirthInfoSolarTime:
    """BirthInfo真太阳时集成测试"""

    def test_normal_mode_no_correction(self):
        """测试普通模式不修正"""
        info = BirthInfo(date="2000-08-16", time_index=6, gender="女")
        assert info.get_adjusted_time_index() == 6

    def test_solar_time_enabled_beijing(self):
        """测试真太阳时模式（北京）"""
        info = BirthInfo(
            date="2000-08-16",
            time_index=6,
            gender="女",
            longitude=116.4,
            use_solar_time=True,
            birth_hour=12,
            birth_minute=0,
        )
        # 北京12:00午时，真太阳时11:46仍是午时
        assert info.get_adjusted_time_index() == 6

    def test_solar_time_enabled_urumqi(self):
        """测试真太阳时模式（乌鲁木齐）"""
        info = BirthInfo(
            date="2000-08-16",
            time_index=6,
            gender="女",
            longitude=87.6,
            use_solar_time=True,
            birth_hour=12,
            birth_minute=0,
        )
        # 乌鲁木齐12:00午时，真太阳时9:50变为巳时
        assert info.get_adjusted_time_index() == 5

    def test_solar_time_validation_no_longitude(self):
        """测试启用真太阳时但未提供经度"""
        with pytest.raises(ValueError) as exc_info:
            BirthInfo(
                date="2000-08-16",
                time_index=6,
                gender="女",
                use_solar_time=True,  # 启用但未提供经度
            )
        assert "经度" in str(exc_info.value)

    def test_solar_time_info_string(self):
        """测试真太阳时信息字符串"""
        info = BirthInfo(
            date="2000-08-16",
            time_index=6,
            gender="女",
            longitude=116.4,
            use_solar_time=True,
            birth_hour=12,
            birth_minute=0,
        )
        info_str = info.get_solar_time_info()
        assert info_str is not None
        assert "北京时间" in info_str
        assert "真太阳时" in info_str
        assert "116.4°E" in info_str

    def test_solar_time_info_none_when_disabled(self):
        """测试禁用真太阳时时信息为None"""
        info = BirthInfo(date="2000-08-16", time_index=6, gender="女")
        assert info.get_solar_time_info() is None

    def test_to_dict_with_solar_time(self):
        """测试包含真太阳时的字典转换"""
        info = BirthInfo(
            date="2000-08-16",
            time_index=6,
            gender="女",
            longitude=116.4,
            latitude=39.9,
            use_solar_time=True,
            birth_hour=12,
            birth_minute=0,
        )
        data = info.to_dict()
        assert data["longitude"] == 116.4
        assert data["latitude"] == 39.9
        assert data["use_solar_time"] is True
        assert data["birth_hour"] == 12
        assert data["birth_minute"] == 0

    def test_from_dict_with_solar_time(self):
        """测试从字典创建包含真太阳时的对象"""
        data = {
            "date": "2000-08-16",
            "time_index": 6,
            "gender": "女",
            "longitude": 116.4,
            "use_solar_time": True,
            "birth_hour": 12,
            "birth_minute": 0,
        }
        info = BirthInfo.from_dict(data)
        assert info.longitude == 116.4
        assert info.use_solar_time is True
        assert info.birth_hour == 12
        assert info.get_adjusted_time_index() == 6
