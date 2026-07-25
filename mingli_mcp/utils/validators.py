"""
参数验证工具
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from mingli_mcp.core.exceptions import DateRangeError, LanguageNotSupportedError, ValidationError

# 支持的日期范围（农历库限制）
MIN_YEAR = 1900
MAX_YEAR = 2100

# 支持的语言列表
SUPPORTED_LANGUAGES = ["zh-CN", "zh-TW", "en-US", "ja-JP", "ko-KR", "vi-VN"]

# 支持的性别值
SUPPORTED_GENDERS = ["男", "女"]

# 支持的历法类型
SUPPORTED_CALENDARS = ["solar", "lunar"]


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
    # bool 是 int 子类，True/False 不是合法时辰；6.5 这类小数
    # 不能被 int() 静默截断成 6，必须整体拒绝
    if isinstance(time_index, bool):
        return False
    if isinstance(time_index, float) and not time_index.is_integer():
        return False
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


def validate_calendar_strict(calendar: Any) -> None:
    """
    严格验证历法类型，失败时抛出异常

    Args:
        calendar: 历法类型

    Raises:
        ValidationError: 历法类型无效

    Note:
        未验证的历法值会被静默当作阳历处理，导致排盘结果错误却不报错，
        因此必须在服务端校验，不能只依赖客户端遵守inputSchema的enum。
    """
    if not isinstance(calendar, str) or calendar not in SUPPORTED_CALENDARS:
        raise ValidationError(
            f"历法类型无效: 值 '{calendar}' 不是有效的历法 "
            f"(支持的值: {', '.join(SUPPORTED_CALENDARS)})"
        )


def validate_solar_time_params(birth_info: Dict[str, Any]) -> None:
    """
    验证真太阳时相关的可选参数

    Args:
        birth_info: 生辰信息字典

    Raises:
        ValidationError: 参数类型或范围无效

    Note:
        inputSchema声明了minimum/maximum，但MCP客户端不保证做校验，
        因此服务端必须自行兜底，否则超范围经度会一路传到时间计算里。
    """
    numeric_ranges = {
        "longitude": (-180.0, 180.0, "经度"),
        "latitude": (-90.0, 90.0, "纬度"),
    }
    for key, (low, high, label) in numeric_ranges.items():
        value = birth_info.get(key)
        if value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValidationError(f"{label}无效: 值 '{value}' 不是数字")
        if not low <= float(value) <= high:
            raise ValidationError(
                f"{label}超出范围: 值 '{value}' 不在有效范围内 (期望: {low} 至 {high})"
            )

    integer_ranges = {
        "birth_hour": (0, 23, "小时"),
        "birth_minute": (0, 59, "分钟"),
    }
    for key, (low_i, high_i, label) in integer_ranges.items():
        value = birth_info.get(key)
        if value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValidationError(f"{label}无效: 值 '{value}' 不是整数")
        if not low_i <= value <= high_i:
            raise ValidationError(
                f"{label}超出范围: 值 '{value}' 不在有效范围内 (期望: {low_i}-{high_i})"
            )

    # 启用真太阳时必须有经度，否则修正会被静默跳过
    if birth_info.get("use_solar_time", False) and birth_info.get("longitude") is None:
        raise ValidationError("启用真太阳时（use_solar_time=true）时必须提供经度（longitude）")


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
            raise ValidationError("缺少必需参数:\n" + "\n".join(missing_details))
        else:
            raise ValidationError(f"缺少必需参数: {', '.join(missing_params)}")
