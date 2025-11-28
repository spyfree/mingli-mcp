#!/usr/bin/env python3
"""
验证器测试
"""

import pytest

from core.exceptions import DateRangeError, LanguageNotSupportedError, ValidationError
from utils.validators import (
    validate_date,
    validate_date_range,
    validate_gender,
    validate_language,
    validate_time_index,
)


class TestDateValidation:
    """日期验证测试"""

    def test_valid_date(self):
        """测试有效日期"""
        assert validate_date("2000-08-16") is True
        assert validate_date("1900-01-01") is True
        assert validate_date("2100-12-31") is True

    def test_invalid_date_format(self):
        """测试无效日期格式"""
        assert validate_date("2000/08/16") is False
        assert validate_date("08-16-2000") is False
        assert validate_date("invalid") is False
        assert validate_date("") is False
        assert validate_date("2000-13-01") is False  # 无效月份
        assert validate_date("2000-02-30") is False  # 无效日期

    def test_date_range_valid(self):
        """测试有效日期范围"""
        # 应该不抛出异常
        validate_date_range("2000-08-16")
        validate_date_range("1900-01-01")
        validate_date_range("2100-12-31")

    def test_date_range_too_early(self):
        """测试日期过早"""
        with pytest.raises(DateRangeError) as exc_info:
            validate_date_range("1899-12-31")
        error_msg = str(exc_info.value)
        assert "1899-12-31" in error_msg  # Should include the invalid value
        assert "1900" in error_msg and "2100" in error_msg  # Should include valid range

    def test_date_range_too_late(self):
        """测试日期过晚"""
        with pytest.raises(DateRangeError) as exc_info:
            validate_date_range("2101-01-01")
        error_msg = str(exc_info.value)
        assert "2101-01-01" in error_msg  # Should include the invalid value
        assert "1900" in error_msg and "2100" in error_msg  # Should include valid range

    def test_date_range_invalid_format(self):
        """测试无效格式"""
        with pytest.raises(ValidationError) as exc_info:
            validate_date_range("invalid-date")
        assert "日期格式错误" in str(exc_info.value)


class TestTimeIndexValidation:
    """时辰验证测试"""

    def test_valid_time_index(self):
        """测试有效时辰"""
        assert validate_time_index(0) is True
        assert validate_time_index(6) is True
        assert validate_time_index(12) is True
        assert validate_time_index("6") is True  # 字符串数字

    def test_invalid_time_index(self):
        """测试无效时辰"""
        assert validate_time_index(-1) is False
        assert validate_time_index(13) is False
        assert validate_time_index("invalid") is False
        assert validate_time_index(None) is False
        assert validate_time_index(100) is False


class TestGenderValidation:
    """性别验证测试"""

    def test_valid_gender(self):
        """测试有效性别"""
        assert validate_gender("男") is True
        assert validate_gender("女") is True

    def test_invalid_gender(self):
        """测试无效性别"""
        assert validate_gender("male") is False
        assert validate_gender("M") is False
        assert validate_gender("") is False
        assert validate_gender("其他") is False


class TestLanguageValidation:
    """语言验证测试"""

    def test_valid_language(self):
        """测试有效语言"""
        # 应该不抛出异常
        validate_language("zh-CN")
        validate_language("zh-TW")
        validate_language("en-US")
        validate_language("ja-JP")
        validate_language("ko-KR")
        validate_language("vi-VN")

    def test_invalid_language(self):
        """测试无效语言"""
        with pytest.raises(LanguageNotSupportedError) as exc_info:
            validate_language("fr-FR")
        assert "fr-FR" in str(exc_info.value)
        assert "zh-CN" in str(exc_info.value)  # 应该列出支持的语言

        with pytest.raises(LanguageNotSupportedError):
            validate_language("invalid")

        with pytest.raises(LanguageNotSupportedError):
            validate_language("")
