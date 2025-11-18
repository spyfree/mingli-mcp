#!/usr/bin/env python3
"""
边界条件测试
"""

import pytest

from core.exceptions import ValidationError


class TestBoundaryConditions:
    """边界条件测试"""

    def test_time_index_boundaries(self):
        """测试时辰边界值"""
        from utils.validators import validate_time_index

        # 边界值
        assert validate_time_index(0) is True  # 早子时
        assert validate_time_index(12) is True  # 晚子时

        # 超出边界
        assert validate_time_index(-1) is False
        assert validate_time_index(13) is False

    def test_date_boundaries(self):
        """测试日期边界值"""
        from utils.validators import validate_date_range

        # 边界值（不应抛出异常）
        validate_date_range("1900-01-01")  # 最小年份
        validate_date_range("2100-12-31")  # 最大年份

        # 超出边界
        with pytest.raises(Exception):
            validate_date_range("1899-12-31")

        with pytest.raises(Exception):
            validate_date_range("2101-01-01")

    def test_leap_year_dates(self):
        """测试闰年日期"""
        from utils.validators import validate_date

        # 闰年2月29日
        assert validate_date("2000-02-29") is True
        assert validate_date("2004-02-29") is True

        # 非闰年2月29日
        assert validate_date("2001-02-29") is False
        assert validate_date("1900-02-29") is False  # 1900不是闰年

    def test_empty_inputs(self):
        """测试空输入"""
        from utils.validators import validate_date, validate_gender

        assert validate_date("") is False
        assert validate_gender("") is False

    def test_special_characters(self):
        """测试特殊字符输入"""
        from utils.validators import validate_date

        assert validate_date("2000-08-16; DROP TABLE") is False
        assert validate_date("../../etc/passwd") is False
        assert validate_date("<script>alert('xss')</script>") is False

    def test_unicode_inputs(self):
        """测试Unicode输入"""
        from utils.validators import validate_gender

        # 有效中文
        assert validate_gender("男") is True
        assert validate_gender("女") is True

        # 无效字符
        assert validate_gender("👨") is False
        assert validate_gender("♂") is False


class TestBirthInfoValidation:
    """生辰信息验证测试"""

    def test_missing_required_fields(self):
        """测试缺少必需字段"""
        from core.base_system import BaseFortuneSystem
        from core.exceptions import ValidationError

        # 创建模拟系统
        class MockSystem(BaseFortuneSystem):
            def get_system_name(self):
                return "Mock"

            def get_system_version(self):
                return "1.0"

            def get_chart(self, birth_info, language="zh-CN"):
                return {}

            def get_fortune(self, birth_info, query_date=None, language="zh-CN"):
                return {}

            def analyze_palace(self, birth_info, palace_name, language="zh-CN"):
                return {}

        system = MockSystem()

        # 测试缺少date
        with pytest.raises(ValidationError) as exc_info:
            system.validate_birth_info({"time_index": 2, "gender": "女"})
        assert "date" in str(exc_info.value)

        # 测试缺少time_index
        with pytest.raises(ValidationError) as exc_info:
            system.validate_birth_info({"date": "2000-08-16", "gender": "女"})
        assert "time_index" in str(exc_info.value)

        # 测试缺少gender
        with pytest.raises(ValidationError) as exc_info:
            system.validate_birth_info({"date": "2000-08-16", "time_index": 2})
        assert "gender" in str(exc_info.value)

    def test_invalid_field_values(self):
        """测试无效字段值"""
        from core.base_system import BaseFortuneSystem
        from core.exceptions import ValidationError

        class MockSystem(BaseFortuneSystem):
            def get_system_name(self):
                return "Mock"

            def get_system_version(self):
                return "1.0"

            def get_chart(self, birth_info, language="zh-CN"):
                return {}

            def get_fortune(self, birth_info, query_date=None, language="zh-CN"):
                return {}

            def analyze_palace(self, birth_info, palace_name, language="zh-CN"):
                return {}

        system = MockSystem()

        # 测试无效时辰
        with pytest.raises(ValidationError):
            system.validate_birth_info(
                {"date": "2000-08-16", "time_index": 13, "gender": "女"}
            )

        # 测试无效性别
        with pytest.raises(ValidationError):
            system.validate_birth_info(
                {"date": "2000-08-16", "time_index": 2, "gender": "M"}
            )
