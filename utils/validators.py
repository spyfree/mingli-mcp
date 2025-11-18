"""
参数验证工具
"""

from datetime import datetime
from typing import Any

from core.exceptions import DateRangeError, LanguageNotSupportedError, ValidationError

# 支持的日期范围（农历库限制）
MIN_YEAR = 1900
MAX_YEAR = 2100

# 支持的语言列表
SUPPORTED_LANGUAGES = ["zh-CN", "zh-TW", "en-US", "ja-JP", "ko-KR", "vi-VN"]


def validate_date(date_str: str) -> bool:
    """
    验证日期格式

    Args:
        date_str: 日期字符串 YYYY-MM-DD

    Returns:
        是否有效
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_date_range(date_str: str) -> None:
    """
    验证日期是否在支持范围内

    Args:
        date_str: 日期字符串 YYYY-MM-DD

    Raises:
        DateRangeError: 日期超出支持范围
        ValidationError: 日期格式错误
    """
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        if not (MIN_YEAR <= dt.year <= MAX_YEAR):
            raise DateRangeError(f"日期超出支持范围（{MIN_YEAR}-{MAX_YEAR}）: {date_str}")
    except ValueError as e:
        raise ValidationError(f"日期格式错误: {date_str}，应为 YYYY-MM-DD 格式") from e


def validate_time_index(time_index: Any) -> bool:
    """
    验证时辰序号

    Args:
        time_index: 时辰序号

    Returns:
        是否有效
    """
    try:
        index = int(time_index)
        return 0 <= index <= 12
    except (ValueError, TypeError):
        return False


def validate_gender(gender: str) -> bool:
    """
    验证性别

    Args:
        gender: 性别字符串

    Returns:
        是否有效
    """
    return gender in ["男", "女"]


def validate_language(language: str) -> None:
    """
    验证语言是否支持

    Args:
        language: 语言代码

    Raises:
        LanguageNotSupportedError: 语言不支持
    """
    if language not in SUPPORTED_LANGUAGES:
        raise LanguageNotSupportedError(
            f"不支持的语言: {language}。支持的语言: {', '.join(SUPPORTED_LANGUAGES)}"
        )
