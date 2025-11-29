"""
MCP Tool definitions.

This module contains all tool schema definitions for the MCP server.
"""

from typing import Any, Dict, List


def get_ziwei_chart_definition() -> Dict[str, Any]:
    """Get definition for get_ziwei_chart tool"""
    return {
        "name": "get_ziwei_chart",
        "description": "获取紫微斗数排盘信息，包含命盘十二宫、主星、辅星、四化等详细信息",
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "出生日期，格式：YYYY-MM-DD，例如：2000-08-16",
                },
                "time_index": {
                    "type": "integer",
                    "description": "出生时辰序号（0-12）",
                    "minimum": 0,
                    "maximum": 12,
                },
                "gender": {
                    "type": "string",
                    "enum": ["男", "女"],
                    "description": "性别：男 或 女",
                },
                "calendar": {
                    "type": "string",
                    "enum": ["solar", "lunar"],
                    "default": "solar",
                    "description": "历法类型：solar(阳历) 或 lunar(农历)",
                },
                "is_leap_month": {
                    "type": "boolean",
                    "default": False,
                    "description": "是否为闰月（仅当calendar=lunar时有效）",
                },
                "format": {
                    "type": "string",
                    "enum": ["json", "markdown"],
                    "default": "markdown",
                },
                "language": {
                    "type": "string",
                    "enum": ["zh-CN", "zh-TW", "en-US", "ja-JP", "ko-KR", "vi-VN"],
                    "default": "zh-CN",
                },
                "longitude": {
                    "type": "number",
                    "description": "出生地经度，用于真太阳时修正",
                    "minimum": -180,
                    "maximum": 180,
                },
                "latitude": {
                    "type": "number",
                    "description": "出生地纬度",
                    "minimum": -90,
                    "maximum": 90,
                },
                "use_solar_time": {
                    "type": "boolean",
                    "default": False,
                    "description": "是否启用真太阳时修正",
                },
                "birth_hour": {
                    "type": "integer",
                    "description": "精确出生小时（0-23）",
                    "minimum": 0,
                    "maximum": 23,
                },
                "birth_minute": {
                    "type": "integer",
                    "description": "精确出生分钟（0-59）",
                    "minimum": 0,
                    "maximum": 59,
                },
            },
            "required": ["date", "time_index", "gender"],
        },
    }


def get_ziwei_fortune_definition() -> Dict[str, Any]:
    """Get definition for get_ziwei_fortune tool"""
    return {
        "name": "get_ziwei_fortune",
        "description": "获取紫微斗数运势信息，包含大限、流年、流月、流日、流时的运势详情",
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "birth_date": {
                    "type": "string",
                    "description": "出生日期，格式：YYYY-MM-DD",
                },
                "time_index": {
                    "type": "integer",
                    "description": "出生时辰序号（0-12）",
                    "minimum": 0,
                    "maximum": 12,
                },
                "gender": {
                    "type": "string",
                    "enum": ["男", "女"],
                    "description": "性别：男 或 女",
                },
                "calendar": {
                    "type": "string",
                    "enum": ["solar", "lunar"],
                    "default": "solar",
                },
                "is_leap_month": {
                    "type": "boolean",
                    "default": False,
                },
                "query_date": {
                    "type": "string",
                    "description": "查询运势的日期，格式：YYYY-MM-DD",
                },
                "format": {
                    "type": "string",
                    "enum": ["json", "markdown"],
                    "default": "markdown",
                },
                "language": {
                    "type": "string",
                    "enum": ["zh-CN", "zh-TW", "en-US", "ja-JP", "ko-KR", "vi-VN"],
                    "default": "zh-CN",
                },
            },
            "required": ["birth_date", "time_index", "gender"],
        },
    }


def get_analyze_ziwei_palace_definition() -> Dict[str, Any]:
    """Get definition for analyze_ziwei_palace tool"""
    return {
        "name": "analyze_ziwei_palace",
        "description": "分析紫微斗数特定宫位的详细信息",
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "birth_date": {
                    "type": "string",
                    "description": "出生日期，格式：YYYY-MM-DD",
                },
                "time_index": {
                    "type": "integer",
                    "description": "出生时辰序号（0-12）",
                    "minimum": 0,
                    "maximum": 12,
                },
                "gender": {
                    "type": "string",
                    "enum": ["男", "女"],
                },
                "palace_name": {
                    "type": "string",
                    "enum": [
                        "命宫",
                        "兄弟宫",
                        "夫妻宫",
                        "子女宫",
                        "财帛宫",
                        "疾厄宫",
                        "迁移宫",
                        "交友宫",
                        "官禄宫",
                        "田宅宫",
                        "福德宫",
                        "父母宫",
                    ],
                    "description": "要分析的宫位名称",
                },
                "calendar": {
                    "type": "string",
                    "enum": ["solar", "lunar"],
                    "default": "solar",
                },
                "is_leap_month": {
                    "type": "boolean",
                    "default": False,
                },
                "format": {
                    "type": "string",
                    "enum": ["json", "markdown"],
                    "default": "markdown",
                },
                "language": {
                    "type": "string",
                    "enum": ["zh-CN", "zh-TW", "en-US", "ja-JP", "ko-KR", "vi-VN"],
                    "default": "zh-CN",
                },
            },
            "required": ["birth_date", "time_index", "gender", "palace_name"],
        },
    }


def get_list_fortune_systems_definition() -> Dict[str, Any]:
    """Get definition for list_fortune_systems tool"""
    return {
        "name": "list_fortune_systems",
        "description": "列出所有可用的命理系统（紫微斗数、八字、占星等）",
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "detailed": {
                    "type": "boolean",
                    "description": "是否输出更详细信息",
                    "default": False,
                }
            },
            "required": [],
            "additionalProperties": False,
        },
    }


def get_bazi_chart_definition() -> Dict[str, Any]:
    """Get definition for get_bazi_chart tool"""
    return {
        "name": "get_bazi_chart",
        "description": "获取八字（四柱）排盘信息，包含年月日时四柱、十神、五行、地支藏干等详细信息",
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "出生日期，格式：YYYY-MM-DD",
                },
                "time_index": {
                    "type": "integer",
                    "description": "出生时辰序号（0-12）",
                    "minimum": 0,
                    "maximum": 12,
                },
                "gender": {
                    "type": "string",
                    "enum": ["男", "女"],
                },
                "calendar": {
                    "type": "string",
                    "enum": ["solar", "lunar"],
                    "default": "solar",
                },
                "is_leap_month": {
                    "type": "boolean",
                    "default": False,
                },
                "format": {
                    "type": "string",
                    "enum": ["json", "markdown"],
                    "default": "markdown",
                },
                "language": {
                    "type": "string",
                    "enum": ["zh-CN", "zh-TW", "en-US", "ja-JP", "ko-KR", "vi-VN"],
                    "default": "zh-CN",
                },
            },
            "required": ["date", "time_index", "gender"],
        },
    }


def get_bazi_fortune_definition() -> Dict[str, Any]:
    """Get definition for get_bazi_fortune tool"""
    return {
        "name": "get_bazi_fortune",
        "description": "获取八字运势信息，包含大运、流年等详情",
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "birth_date": {
                    "type": "string",
                    "description": "出生日期，格式：YYYY-MM-DD",
                },
                "time_index": {
                    "type": "integer",
                    "description": "出生时辰序号（0-12）",
                    "minimum": 0,
                    "maximum": 12,
                },
                "gender": {
                    "type": "string",
                    "enum": ["男", "女"],
                },
                "calendar": {
                    "type": "string",
                    "enum": ["solar", "lunar"],
                    "default": "solar",
                },
                "is_leap_month": {
                    "type": "boolean",
                    "default": False,
                },
                "query_date": {
                    "type": "string",
                    "description": "查询运势的日期，格式：YYYY-MM-DD",
                },
                "format": {
                    "type": "string",
                    "enum": ["json", "markdown"],
                    "default": "markdown",
                },
                "language": {
                    "type": "string",
                    "enum": ["zh-CN", "zh-TW", "en-US", "ja-JP", "ko-KR", "vi-VN"],
                    "default": "zh-CN",
                },
            },
            "required": ["birth_date", "time_index", "gender"],
        },
    }


def get_analyze_bazi_element_definition() -> Dict[str, Any]:
    """Get definition for analyze_bazi_element tool"""
    return {
        "name": "analyze_bazi_element",
        "description": "分析八字五行强弱，包含五行分数、平衡度、缺失五行等",
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "birth_date": {
                    "type": "string",
                    "description": "出生日期，格式：YYYY-MM-DD",
                },
                "time_index": {
                    "type": "integer",
                    "description": "出生时辰序号（0-12）",
                    "minimum": 0,
                    "maximum": 12,
                },
                "gender": {
                    "type": "string",
                    "enum": ["男", "女"],
                },
                "calendar": {
                    "type": "string",
                    "enum": ["solar", "lunar"],
                    "default": "solar",
                },
                "is_leap_month": {
                    "type": "boolean",
                    "default": False,
                },
                "format": {
                    "type": "string",
                    "enum": ["json", "markdown"],
                    "default": "markdown",
                },
                "language": {
                    "type": "string",
                    "enum": ["zh-CN", "zh-TW", "en-US", "ja-JP", "ko-KR", "vi-VN"],
                    "default": "zh-CN",
                },
            },
            "required": ["birth_date", "time_index", "gender"],
        },
    }


def get_all_tool_definitions() -> List[Dict[str, Any]]:
    """Get all tool definitions"""
    return [
        get_ziwei_chart_definition(),
        get_ziwei_fortune_definition(),
        get_analyze_ziwei_palace_definition(),
        get_list_fortune_systems_definition(),
        get_bazi_chart_definition(),
        get_bazi_fortune_definition(),
        get_analyze_bazi_element_definition(),
    ]
