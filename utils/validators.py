"""
参数验证工具
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from core.exceptions import DateRangeError, LanguageNotSupportedError, ValidationError

# 支持的日期范围（农历库限制）
MIN_YEAR = 1900
MAX_YEAR = 2100

# 支持的语言列表
SUPPORTED_LANGUAGES = ["zh-CN", "zh-TW", "en-US", "ja-JP", "ko-KR", "vi-VN"]

# 支持的性别值
SUPPORTED_GENDERS = ["男", "女"]


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
            raise DateRangeError(
                f"日期超出支持范围: 值 '{date_str}' 不在有效范围内 "
                f"(期望: {MIN_YEAR}-01-01 至 {MAX_YEAR}-12-31)"
            )
    except ValueError as e:
        raise ValidationError(
            f"日期格式错误: 值 '{date_str}' 格式无效 (期望格式: YYYY-MM-DD)"
        ) from e


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


def validate_time_index_strict(time_index: Any) -> None:
    """
    严格验证时辰序号，失败时抛出异常

    Args:
        time_index: 时辰序号

    Raises:
        ValidationError: 时辰序号无效
    """
    if not validate_time_index(time_index):
        raise ValidationError(f"时辰序号无效: 值 '{time_index}' 不在有效范围内 (期望: 0-12 的整数)")


def validate_gender(gender: str) -> bool:
    """
    验证性别

    Args:
        gender: 性别字符串

    Returns:
        是否有效
    """
    return gender in SUPPORTED_GENDERS


def validate_gender_strict(gender: Any) -> None:
    """
    严格验证性别，失败时抛出异常

    Args:
        gender: 性别字符串

    Raises:
        ValidationError: 性别无效
    """
    if not isinstance(gender, str) or gender not in SUPPORTED_GENDERS:
        raise ValidationError(
            f"性别无效: 值 '{gender}' 不是有效的性别 " f"(支持的值: {', '.join(SUPPORTED_GENDERS)})"
        )


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
            f"不支持的语言: 值 '{language}' 不是有效的语言代码 "
            f"(支持的语言: {', '.join(SUPPORTED_LANGUAGES)})"
        )


def validate_required_params(
    args: Dict[str, Any],
    required_params: List[str],
    param_descriptions: Optional[Dict[str, str]] = None,
) -> None:
    """
    验证必需参数是否存在

    Args:
        args: 参数字典
        required_params: 必需参数列表
        param_descriptions: 参数描述字典（可选）

    Raises:
        ValidationError: 缺少必需参数
    """
    missing_params = [p for p in required_params if p not in args or args[p] is None]

    if missing_params:
        if param_descriptions:
            missing_details = [
                f"  - {p}: {param_descriptions.get(p, '必需参数')}" for p in missing_params
            ]
            raise ValidationError(f"缺少必需参数:\n" + "\n".join(missing_details))
        else:
            raise ValidationError(f"缺少必需参数: {', '.join(missing_params)}")
