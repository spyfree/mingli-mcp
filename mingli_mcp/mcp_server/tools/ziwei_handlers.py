"""
Ziwei (紫微斗数) tool handlers.

This module contains handlers for Ziwei-related MCP tools.
"""

import json
from datetime import datetime
from typing import Any, Dict, List

from mingli_mcp.core.exceptions import ValidationError
from mingli_mcp.mcp_server.tools.arguments import normalize_birth_date
from mingli_mcp.systems import get_system
from mingli_mcp.systems.ziwei.formatter import ZiweiFormatter
from mingli_mcp.utils.fortune_time import annual_markdown, calendar_year_fortune
from mingli_mcp.utils.performance import PerformanceTimer, log_performance
from mingli_mcp.utils.validators import (
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
    "birth_date": "出生日期 (格式: YYYY-MM-DD)",
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
    date_key: str = "birth_date",
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


def _build_birth_info(args: Dict[str, Any], date_key: str = "birth_date") -> Dict[str, Any]:
    """构建生辰信息字典"""
    birth_info = {
        "date": args[date_key],
        "time_index": args["time_index"],
        "gender": args["gender"],
        "calendar": args.get("calendar", "solar"),
        "is_leap_month": args.get("is_leap_month", False),
    }

    # 真太阳时修正相关的可选参数需要透传给排盘系统
    for key in ("longitude", "latitude", "use_solar_time", "birth_hour", "birth_minute"):
        if args.get(key) is not None:
            birth_info[key] = args[key]

    return birth_info


def _to_json(data: Any) -> str:
    """序列化为JSON文本（MCP的content.text必须是字符串）"""
    return json.dumps(data, ensure_ascii=False, indent=2)


@log_performance
def handle_get_ziwei_chart(args: Dict[str, Any]) -> str:
    """工具：获取紫微斗数排盘"""
    args = normalize_birth_date(args)
    # Validate parameters
    _validate_common_params(
        args, ["birth_date", "time_index", "gender"], ZIWEI_CHART_PARAM_DESCRIPTIONS
    )

    with PerformanceTimer("紫微排盘"):
        birth_info = _build_birth_info(args)
        language = args.get("language", "zh-CN")

        system = get_system("ziwei")
        chart = system.get_chart(birth_info, language)

        output_format = args.get("format", "markdown")
        if output_format == "json":
            return _to_json(chart)
        else:
            return _ziwei_formatter.format_chart_markdown(chart)


@log_performance
def handle_get_ziwei_fortune(args: Dict[str, Any]) -> str:
    """工具：获取紫微斗数运势"""
    args = normalize_birth_date(args)
    # Validate parameters
    _validate_common_params(
        args,
        ["birth_date", "time_index", "gender"],
        ZIWEI_FORTUNE_PARAM_DESCRIPTIONS,
    )

    with PerformanceTimer("紫微运势查询"):
        birth_info = _build_birth_info(args)

        if "query_year" in args:
            if "query_date" in args:
                raise ValidationError("query_year 与 query_date 不能同时提供")
            system = get_system("ziwei")
            result = calendar_year_fortune(
                args["query_year"],
                "ziwei",
                lambda date: system.get_fortune(birth_info, date, args.get("language", "zh-CN")),
            )
            return _to_json(result) if args.get("format") == "json" else annual_markdown(result)
        if "query_date" in args and not args["query_date"]:
            raise ValidationError("query_date 不能为空；查询全年请使用 query_year")
        query_date_str = args.get("query_date")
        if query_date_str:
            validate_date_range(query_date_str)
            query_date = datetime.strptime(query_date_str, "%Y-%m-%d")
        else:
            query_date = datetime.now()

        language = args.get("language", "zh-CN")
        system = get_system("ziwei")
        fortune = system.get_fortune(birth_info, query_date, language)

        output_format = args.get("format", "markdown")
        if output_format == "json":
            return _to_json(fortune)
        else:
            return _ziwei_formatter.format_fortune_markdown(fortune)


@log_performance
def handle_analyze_ziwei_palace(args: Dict[str, Any]) -> str:
    """工具：分析紫微斗数宫位"""
    args = normalize_birth_date(args)
    # Validate parameters
    _validate_common_params(
        args,
        ["birth_date", "time_index", "gender", "palace_name"],
        ZIWEI_PALACE_PARAM_DESCRIPTIONS,
    )

    with PerformanceTimer("紫微宫位分析"):
        birth_info = _build_birth_info(args)
        palace_name = args["palace_name"]
        language = args.get("language", "zh-CN")

        system = get_system("ziwei")
        analysis = system.analyze_palace(birth_info, palace_name, language)

        output_format = args.get("format", "markdown")
        if output_format == "json":
            return _to_json(analysis)
        else:
            return _ziwei_formatter.format_palace_analysis_markdown(analysis)
