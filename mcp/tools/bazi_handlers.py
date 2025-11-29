"""
Bazi (八字) tool handlers.

This module contains handlers for Bazi-related MCP tools.
"""

import json
from datetime import datetime
from typing import Any, Dict, List

from systems import get_system
from systems.bazi.formatter import BaziFormatter
from utils.performance import PerformanceTimer, log_performance
from utils.validators import (
    validate_date_range,
    validate_gender_strict,
    validate_language,
    validate_required_params,
    validate_time_index_strict,
)

# Shared formatter instance
_bazi_formatter = BaziFormatter()

# Parameter descriptions for error messages
BAZI_CHART_PARAM_DESCRIPTIONS = {
    "date": "出生日期 (格式: YYYY-MM-DD)",
    "time_index": "出生时辰序号 (0-12)",
    "gender": "性别 (男/女)",
}

BAZI_FORTUNE_PARAM_DESCRIPTIONS = {
    "birth_date": "出生日期 (格式: YYYY-MM-DD)",
    "time_index": "出生时辰序号 (0-12)",
    "gender": "性别 (男/女)",
}

BAZI_ELEMENT_PARAM_DESCRIPTIONS = {
    "birth_date": "出生日期 (格式: YYYY-MM-DD)",
    "time_index": "出生时辰序号 (0-12)",
    "gender": "性别 (男/女)",
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
def handle_get_bazi_chart(args: Dict[str, Any]) -> str:
    """工具：获取八字排盘"""
    # Validate parameters
    _validate_common_params(
        args, ["date", "time_index", "gender"], BAZI_CHART_PARAM_DESCRIPTIONS, date_key="date"
    )

    with PerformanceTimer("八字排盘"):
        birth_info = _build_birth_info(args)
        language = args.get("language", "zh-CN")

        system = get_system("bazi")
        chart = system.get_chart(birth_info, language)

        output_format = args.get("format", "markdown")
        if output_format == "json":
            return _format_response(chart, "json")
        else:
            return _bazi_formatter.format_chart(chart, "markdown")


@log_performance
def handle_get_bazi_fortune(args: Dict[str, Any]) -> str:
    """工具：获取八字运势"""
    # Validate parameters
    _validate_common_params(
        args,
        ["birth_date", "time_index", "gender"],
        BAZI_FORTUNE_PARAM_DESCRIPTIONS,
        date_key="birth_date",
    )

    with PerformanceTimer("八字运势查询"):
        birth_info = _build_birth_info(args, date_key="birth_date")

        query_date_str = args.get("query_date")
        if query_date_str:
            query_date = datetime.strptime(query_date_str, "%Y-%m-%d")
        else:
            query_date = datetime.now()

        language = args.get("language", "zh-CN")
        system = get_system("bazi")
        fortune = system.get_fortune(birth_info, query_date, language)

        output_format = args.get("format", "markdown")
        if output_format == "json":
            return _format_response(fortune, "json")
        else:
            return _bazi_formatter.format_fortune(fortune, "markdown")


@log_performance
def handle_analyze_bazi_element(args: Dict[str, Any]) -> str:
    """工具：分析八字五行"""
    # Validate parameters
    _validate_common_params(
        args,
        ["birth_date", "time_index", "gender"],
        BAZI_ELEMENT_PARAM_DESCRIPTIONS,
        date_key="birth_date",
    )

    with PerformanceTimer("八字五行分析"):
        birth_info = _build_birth_info(args, date_key="birth_date")

        system = get_system("bazi")
        analysis = system.analyze_element(birth_info)

        output_format = args.get("format", "markdown")
        if output_format == "json":
            return _format_response(analysis, "json")
        else:
            return _bazi_formatter.format_element_analysis(analysis, "markdown")
