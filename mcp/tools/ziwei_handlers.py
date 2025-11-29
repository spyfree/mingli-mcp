"""
Ziwei (紫微斗数) tool handlers.

This module contains handlers for Ziwei-related MCP tools.
"""

import json
from datetime import datetime
from typing import Any, Dict, List

from systems import get_system
from systems.ziwei.formatter import ZiweiFormatter
from utils.performance import PerformanceTimer, log_performance
from utils.validators import (
    validate_date_range,
    validate_gender_strict,
    validate_language,
    validate_required_params,
    validate_time_index_strict,
)

# Shared formatter instance
_ziwei_formatter = ZiweiFormatter()

# Parameter descriptions for error messages
ZIWEI_CHART_PARAM_DESCRIPTIONS = {
    "date": "出生日期 (格式: YYYY-MM-DD)",
    "time_index": "出生时辰序号 (0-12)",
    "gender": "性别 (男/女)",
}

ZIWEI_FORTUNE_PARAM_DESCRIPTIONS = {
    "birth_date": "出生日期 (格式: YYYY-MM-DD)",
    "time_index": "出生时辰序号 (0-12)",
    "gender": "性别 (男/女)",
}

ZIWEI_PALACE_PARAM_DESCRIPTIONS = {
    "birth_date": "出生日期 (格式: YYYY-MM-DD)",
    "time_index": "出生时辰序号 (0-12)",
    "gender": "性别 (男/女)",
    "palace_name": "宫位名称",
}


def _validate_common_params(
    args: Dict[str, Any],
    required_params: List[str],
    param_descriptions: Dict[str, str],
    date_key: str = "date",
) -> None:
    """验证通用参数"""
    # Check required params first
    validate_required_params(args, required_params, param_descriptions)

    # Validate individual fields
    validate_date_range(args[date_key])
    validate_time_index_strict(args["time_index"])
    validate_gender_strict(args["gender"])

    # Validate language if provided
    language = args.get("language")
    if language:
        validate_language(language)


def _build_birth_info(args: Dict[str, Any], date_key: str = "date") -> Dict[str, Any]:
    """构建生辰信息字典"""
    return {
        "date": args[date_key],
        "time_index": args["time_index"],
        "gender": args["gender"],
        "calendar": args.get("calendar", "solar"),
        "is_leap_month": args.get("is_leap_month", False),
    }


def _format_response(data: Any, output_format: str) -> str:
    """格式化响应数据"""
    if output_format == "json":
        return json.dumps(data, ensure_ascii=False, indent=2)
    return data


@log_performance
def handle_get_ziwei_chart(args: Dict[str, Any]) -> str:
    """工具：获取紫微斗数排盘"""
    # Validate parameters
    _validate_common_params(
        args, ["date", "time_index", "gender"], ZIWEI_CHART_PARAM_DESCRIPTIONS, date_key="date"
    )

    with PerformanceTimer("紫微排盘"):
        birth_info = _build_birth_info(args)
        language = args.get("language", "zh-CN")

        system = get_system("ziwei")
        chart = system.get_chart(birth_info, language)

        output_format = args.get("format", "markdown")
        if output_format == "json":
            return _format_response(chart, "json")
        else:
            return _ziwei_formatter.format_chart_markdown(chart)


@log_performance
def handle_get_ziwei_fortune(args: Dict[str, Any]) -> str:
    """工具：获取紫微斗数运势"""
    # Validate parameters
    _validate_common_params(
        args,
        ["birth_date", "time_index", "gender"],
        ZIWEI_FORTUNE_PARAM_DESCRIPTIONS,
        date_key="birth_date",
    )

    with PerformanceTimer("紫微运势查询"):
        birth_info = _build_birth_info(args, date_key="birth_date")

        query_date_str = args.get("query_date")
        if query_date_str:
            query_date = datetime.strptime(query_date_str, "%Y-%m-%d")
        else:
            query_date = datetime.now()

        language = args.get("language", "zh-CN")
        system = get_system("ziwei")
        fortune = system.get_fortune(birth_info, query_date, language)

        output_format = args.get("format", "markdown")
        if output_format == "json":
            return _format_response(fortune, "json")
        else:
            return _ziwei_formatter.format_fortune_markdown(fortune)


@log_performance
def handle_analyze_ziwei_palace(args: Dict[str, Any]) -> str:
    """工具：分析紫微斗数宫位"""
    # Validate parameters
    _validate_common_params(
        args,
        ["birth_date", "time_index", "gender", "palace_name"],
        ZIWEI_PALACE_PARAM_DESCRIPTIONS,
        date_key="birth_date",
    )

    with PerformanceTimer("紫微宫位分析"):
        birth_info = _build_birth_info(args, date_key="birth_date")
        palace_name = args["palace_name"]
        language = args.get("language", "zh-CN")

        system = get_system("ziwei")
        analysis = system.analyze_palace(birth_info, palace_name, language)

        output_format = args.get("format", "markdown")
        if output_format == "json":
            return _format_response(analysis, "json")
        else:
            return _ziwei_formatter.format_palace_analysis_markdown(analysis)
