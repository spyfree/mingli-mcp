#!/usr/bin/env python3
"""
命理MCP服务器主入口

支持多种命理系统（紫微斗数、八字、占星等）的MCP集成
支持多种传输方式（stdio、HTTP、WebSocket）
"""

import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from config import config
from core.exceptions import (
    ConfigError,
    SystemError,
    SystemNotFoundError,
    ToolCallError,
    ValidationError,
)
from systems import get_system, list_systems
from systems.bazi.formatter import BaziFormatter
from systems.ziwei.formatter import ZiweiFormatter
from transports import HttpTransport, StdioTransport
from utils.formatters import format_error_response, format_success_response

logger = config.get_logger(__name__)


class MingliMCPServer:
    """命理MCP服务器"""

    # MCP协议版本
    PROTOCOL_VERSION = "2024-11-05"

    def __init__(self):
        self.transport = None
        self.ziwei_formatter = ZiweiFormatter()
        self.bazi_formatter = BaziFormatter()
        self._initialize_transport()

    def _initialize_transport(self):
        """初始化传输层"""
        from transports import HTTP_TRANSPORT_AVAILABLE

        transport_type = config.TRANSPORT_TYPE.lower()

        if transport_type == "stdio":
            self.transport = StdioTransport()
        elif transport_type == "http":
            if not HTTP_TRANSPORT_AVAILABLE:
                raise ImportError(
                    "HTTP transport is not available. Please install mingli-mcp with HTTP support:\n"
                    "  pip install mingli-mcp[http]\n"
                    "or\n"
                    "  pip install mingli-mcp (which includes all dependencies)"
                )
            from transports import HttpTransport
            self.transport = HttpTransport(
                host=config.HTTP_HOST, port=config.HTTP_PORT, api_key=config.HTTP_API_KEY
            )
        # 预留WebSocket传输方式
        # elif transport_type == 'websocket':
        #     self.transport = WebSocketTransport(config.WS_HOST, config.WS_PORT)
        else:
            raise ValueError(f"Unsupported transport type: {transport_type}")

        self.transport.set_message_handler(self.handle_request)
        logger.info(f"Initialized {transport_type} transport")

    def start(self):
        """启动MCP服务器"""
        logger.info(f"Starting {config.MCP_SERVER_NAME} v{config.MCP_SERVER_VERSION}")
        logger.info(f"Available systems: {', '.join(list_systems())}")
        self.transport.start()

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理MCP请求

        Args:
            request: JSON-RPC请求

        Returns:
            JSON-RPC响应
        """
        method = request.get("method")
        request_id = request.get("id")

        try:
            # 初始化请求
            if method == "initialize":
                return self._handle_initialize(request, request_id)

            # 通知消息（无需响应）
            elif method == "notifications/initialized":
                logger.info("Received initialized notification")
                return None

            # 列出工具
            elif method == "tools/list":
                return self._handle_tools_list(request_id)

            # 调用工具
            elif method == "tools/call":
                return self._handle_tools_call(request, request_id)

            # 列出提示词
            elif method == "prompts/list":
                return self._handle_prompts_list(request_id)

            # 获取提示词
            elif method == "prompts/get":
                return self._handle_prompts_get(request, request_id)

            # 未知方法
            else:
                logger.warning(f"Unknown method: {method}")
                return format_error_response(-32601, f"Method not found: {method}", request_id)

        except (ValidationError, SystemNotFoundError) as e:
            logger.error(f"Request validation error for {method}: {e}")
            return format_error_response(-32602, str(e), request_id)
        except Exception as e:
            logger.exception(f"Unexpected error handling request: {method}")
            return format_error_response(-32603, f"Internal error: {str(e)}", request_id)

    def _handle_initialize(self, request: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """处理初始化请求"""
        client_info = request.get("params", {})
        logger.info(f"Client info: {client_info}")

        return format_success_response(
            {
                "protocolVersion": self.PROTOCOL_VERSION,
                "serverInfo": {
                    "name": config.MCP_SERVER_NAME,
                    "version": config.MCP_SERVER_VERSION,
                },
                "capabilities": {
                    "tools": {},
                    "prompts": {},
                },
            },
            request_id,
        )

    def _handle_tools_list(self, request_id: Any) -> Dict[str, Any]:
        """处理工具列表请求"""
        tools = [
            {
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
                            "description": "出生时辰序号（0-12）：0=早子时(23-01), 1=丑时(01-03), 2=寅时(03-05), 3=卯时(05-07), 4=辰时(07-09), 5=巳时(09-11), 6=午时(11-13), 7=未时(13-15), 8=申时(15-17), 9=酉时(17-19), 10=戌时(19-21), 11=亥时(21-23), 12=晚子时(23-01)",
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
                            "description": "历法类型：solar(阳历/公历) 或 lunar(农历/阴历)，默认为阳历",
                        },
                        "is_leap_month": {
                            "type": "boolean",
                            "default": False,
                            "description": "是否为闰月（仅当calendar=lunar时有效），默认为否",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["json", "markdown"],
                            "default": "markdown",
                            "description": "输出格式：json(结构化数据) 或 markdown(易读格式)，默认为markdown",
                        },
                    },
                    "required": ["date", "time_index", "gender"],
                },
            },
            {
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
                        "gender": {"type": "string", "enum": ["男", "女"], "description": "性别"},
                        "calendar": {
                            "type": "string",
                            "enum": ["solar", "lunar"],
                            "default": "solar",
                            "description": "历法类型",
                        },
                        "is_leap_month": {
                            "type": "boolean",
                            "default": False,
                            "description": "是否为闰月",
                        },
                        "query_date": {
                            "type": "string",
                            "description": "查询运势的日期，格式：YYYY-MM-DD，不填则为今天",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["json", "markdown"],
                            "default": "markdown",
                            "description": "输出格式",
                        },
                    },
                    "required": ["birth_date", "time_index", "gender"],
                },
            },
            {
                "name": "analyze_ziwei_palace",
                "description": "分析紫微斗数特定宫位的详细信息，包括该宫位的星曜配置、大限、四化等",
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
                        "gender": {"type": "string", "enum": ["男", "女"], "description": "性别"},
                        "palace_name": {
                            "type": "string",
                            "enum": [
                                "命宫",
                                "兄弟",
                                "夫妻",
                                "子女",
                                "财帛",
                                "疾厄",
                                "迁移",
                                "仆役",
                                "官禄",
                                "田宅",
                                "福德",
                                "父母",
                            ],
                            "description": "要分析的宫位名称",
                        },
                        "calendar": {
                            "type": "string",
                            "enum": ["solar", "lunar"],
                            "default": "solar",
                            "description": "历法类型",
                        },
                        "is_leap_month": {
                            "type": "boolean",
                            "default": False,
                            "description": "是否为闰月",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["json", "markdown"],
                            "default": "markdown",
                            "description": "输出格式",
                        },
                    },
                    "required": ["birth_date", "time_index", "gender", "palace_name"],
                },
            },
            {
                "name": "list_fortune_systems",
                "description": "列出所有可用的命理系统（紫微斗数、八字、占星等）",
                "annotations": {
                    "readOnlyHint": True,
                    "destructiveHint": False,
                    "idempotentHint": True,
                },
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
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
                            "description": "出生日期，格式：YYYY-MM-DD，例如：2000-08-16",
                        },
                        "time_index": {
                            "type": "integer",
                            "description": "出生时辰序号（0-12）：0=早子时(23-01), 1=丑时(01-03), 2=寅时(03-05), 3=卯时(05-07), 4=辰时(07-09), 5=巳时(09-11), 6=午时(11-13), 7=未时(13-15), 8=申时(15-17), 9=酉时(17-19), 10=戌时(19-21), 11=亥时(21-23), 12=晚子时(23-01)",
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
                            "description": "历法类型：solar(阳历/公历) 或 lunar(农历/阴历)，默认为阳历",
                        },
                        "is_leap_month": {
                            "type": "boolean",
                            "default": False,
                            "description": "是否为闰月（仅当calendar=lunar时有效），默认为否",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["json", "markdown"],
                            "default": "markdown",
                            "description": "输出格式：json(结构化数据) 或 markdown(易读格式)，默认为markdown",
                        },
                    },
                    "required": ["date", "time_index", "gender"],
                },
            },
            {
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
                        "gender": {"type": "string", "enum": ["男", "女"], "description": "性别"},
                        "calendar": {
                            "type": "string",
                            "enum": ["solar", "lunar"],
                            "default": "solar",
                            "description": "历法类型",
                        },
                        "is_leap_month": {
                            "type": "boolean",
                            "default": False,
                            "description": "是否为闰月",
                        },
                        "query_date": {
                            "type": "string",
                            "description": "查询运势的日期，格式：YYYY-MM-DD，不填则为今天",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["json", "markdown"],
                            "default": "markdown",
                            "description": "输出格式",
                        },
                    },
                    "required": ["birth_date", "time_index", "gender"],
                },
            },
            {
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
                        "gender": {"type": "string", "enum": ["男", "女"], "description": "性别"},
                        "calendar": {
                            "type": "string",
                            "enum": ["solar", "lunar"],
                            "default": "solar",
                            "description": "历法类型",
                        },
                        "is_leap_month": {
                            "type": "boolean",
                            "default": False,
                            "description": "是否为闰月",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["json", "markdown"],
                            "default": "markdown",
                            "description": "输出格式",
                        },
                    },
                    "required": ["birth_date", "time_index", "gender"],
                },
            },
        ]

        return format_success_response({"tools": tools}, request_id)

    def _handle_tools_call(self, request: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """处理工具调用请求"""
        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        logger.info(f"Tool call: {tool_name}")
        logger.debug(f"Arguments: {arguments}")

        try:
            # 紫微斗数排盘
            if tool_name == "get_ziwei_chart":
                result = self._tool_get_ziwei_chart(arguments)

            # 紫微斗数运势
            elif tool_name == "get_ziwei_fortune":
                result = self._tool_get_ziwei_fortune(arguments)

            # 紫微宫位分析
            elif tool_name == "analyze_ziwei_palace":
                result = self._tool_analyze_ziwei_palace(arguments)

            # 列出系统
            elif tool_name == "list_fortune_systems":
                result = self._tool_list_systems()

            # 八字排盘
            elif tool_name == "get_bazi_chart":
                result = self._tool_get_bazi_chart(arguments)

            # 八字运势
            elif tool_name == "get_bazi_fortune":
                result = self._tool_get_bazi_fortune(arguments)

            # 八字五行分析
            elif tool_name == "analyze_bazi_element":
                result = self._tool_analyze_bazi_element(arguments)

            else:
                return format_error_response(-32602, f"Unknown tool: {tool_name}", request_id)

            return format_success_response(
                {"content": [{"type": "text", "text": result}]}, request_id
            )

        except ValidationError as e:
            logger.error(f"Parameter validation error: {e}")
            return format_error_response(-32602, str(e), request_id)

        except SystemNotFoundError as e:
            logger.error(f"System not found: {e}")
            return format_error_response(-32602, str(e), request_id)

        except SystemError as e:
            logger.error(f"System execution error: {e}")
            return format_error_response(-32603, str(e), request_id)

        except ToolCallError as e:
            logger.error(f"Tool call error: {e}")
            return format_error_response(-32603, str(e), request_id)

        except Exception as e:
            logger.exception("Unexpected error in tool call")
            return format_error_response(-32603, f"Internal error: {str(e)}", request_id)

    def _tool_get_ziwei_chart(self, args: Dict[str, Any]) -> str:
        """工具：获取紫微斗数排盘"""
        birth_info = {
            "date": args["date"],
            "time_index": args["time_index"],
            "gender": args["gender"],
            "calendar": args.get("calendar", "solar"),
            "is_leap_month": args.get("is_leap_month", False),
        }

        system = get_system("ziwei")
        chart = system.get_chart(birth_info)

        output_format = args.get("format", "markdown")
        if output_format == "json":
            import json

            return json.dumps(chart, ensure_ascii=False, indent=2)
        else:
            return self.ziwei_formatter.format_chart_markdown(chart)

    def _tool_get_ziwei_fortune(self, args: Dict[str, Any]) -> str:
        """工具：获取紫微斗数运势"""
        birth_info = {
            "date": args["birth_date"],
            "time_index": args["time_index"],
            "gender": args["gender"],
            "calendar": args.get("calendar", "solar"),
            "is_leap_month": args.get("is_leap_month", False),
        }

        # 解析查询日期
        query_date_str = args.get("query_date")
        if query_date_str:
            query_date = datetime.strptime(query_date_str, "%Y-%m-%d")
        else:
            query_date = datetime.now()

        system = get_system("ziwei")
        fortune = system.get_fortune(birth_info, query_date)

        output_format = args.get("format", "markdown")
        if output_format == "json":
            import json

            return json.dumps(fortune, ensure_ascii=False, indent=2)
        else:
            return self.ziwei_formatter.format_fortune_markdown(fortune)

    def _tool_analyze_ziwei_palace(self, args: Dict[str, Any]) -> str:
        """工具：分析紫微斗数宫位"""
        birth_info = {
            "date": args["birth_date"],
            "time_index": args["time_index"],
            "gender": args["gender"],
            "calendar": args.get("calendar", "solar"),
            "is_leap_month": args.get("is_leap_month", False),
        }

        palace_name = args["palace_name"]

        system = get_system("ziwei")
        analysis = system.analyze_palace(birth_info, palace_name)

        output_format = args.get("format", "markdown")
        if output_format == "json":
            import json

            return json.dumps(analysis, ensure_ascii=False, indent=2)
        else:
            return self.ziwei_formatter.format_palace_analysis_markdown(analysis)

    def _tool_list_systems(self) -> str:
        """工具：列出所有命理系统"""
        systems = list_systems()

        result = "# 可用的命理系统\n\n"
        for system_name in systems:
            try:
                system = get_system(system_name)
                capabilities = system.get_capabilities()

                result += f"## {system.get_system_name()}\n\n"
                result += f"- **版本**: {system.get_system_version()}\n"
                result += f"- **系统ID**: {system_name}\n"
                result += "- **功能支持**:\n"
                for cap_name, cap_value in capabilities.items():
                    status = "✅" if cap_value else "❌"
                    result += f"  - {cap_name}: {status}\n"

                if hasattr(system, "get_supported_palaces"):
                    palaces = system.get_supported_palaces()
                    if palaces:
                        result += f"- **支持宫位**: {', '.join(palaces)}\n"

                result += "\n"
            except Exception as e:
                result += f"## {system_name}\n\n"
                result += f"- **状态**: 加载失败 - {str(e)}\n\n"

        return result

    def _tool_get_bazi_chart(self, args: Dict[str, Any]) -> str:
        """工具：获取八字排盘"""
        birth_info = {
            "date": args["date"],
            "time_index": args["time_index"],
            "gender": args["gender"],
            "calendar": args.get("calendar", "solar"),
            "is_leap_month": args.get("is_leap_month", False),
        }

        system = get_system("bazi")
        chart = system.get_chart(birth_info)

        output_format = args.get("format", "markdown")
        if output_format == "json":
            import json

            return json.dumps(chart, ensure_ascii=False, indent=2)
        else:
            return self.bazi_formatter.format_chart(chart, "markdown")

    def _tool_get_bazi_fortune(self, args: Dict[str, Any]) -> str:
        """工具：获取八字运势"""
        birth_info = {
            "date": args["birth_date"],
            "time_index": args["time_index"],
            "gender": args["gender"],
            "calendar": args.get("calendar", "solar"),
            "is_leap_month": args.get("is_leap_month", False),
        }

        # 解析查询日期
        query_date_str = args.get("query_date")
        if query_date_str:
            query_date = datetime.strptime(query_date_str, "%Y-%m-%d")
        else:
            query_date = datetime.now()

        system = get_system("bazi")
        fortune = system.get_fortune(birth_info, query_date)

        output_format = args.get("format", "markdown")
        if output_format == "json":
            import json

            return json.dumps(fortune, ensure_ascii=False, indent=2)
        else:
            return self.bazi_formatter.format_fortune(fortune, "markdown")

    def _tool_analyze_bazi_element(self, args: Dict[str, Any]) -> str:
        """工具：分析八字五行"""
        birth_info = {
            "date": args["birth_date"],
            "time_index": args["time_index"],
            "gender": args["gender"],
            "calendar": args.get("calendar", "solar"),
            "is_leap_month": args.get("is_leap_month", False),
        }

        system = get_system("bazi")
        analysis = system.analyze_element(birth_info)

        output_format = args.get("format", "markdown")
        if output_format == "json":
            import json

            return json.dumps(analysis, ensure_ascii=False, indent=2)
        else:
            return self.bazi_formatter.format_element_analysis(analysis, "markdown")

    def _handle_prompts_list(self, request_id: Any) -> Dict[str, Any]:
        """处理提示词列表请求"""
        import os

        prompts_dir = os.path.join(os.path.dirname(__file__), "prompts")
        prompts = []

        if os.path.exists(prompts_dir):
            for filename in os.listdir(prompts_dir):
                if filename.endswith(".md"):
                    filepath = os.path.join(prompts_dir, filename)
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        # Extract title from first line
                        lines = content.split("\n")
                        title = lines[0].replace("#", "").strip()
                        description = ""
                        # Find description section or use first paragraph
                        for line in lines[1:]:
                            if line.strip() and not line.startswith("#"):
                                description = line.strip()
                                break

                        prompt_name = filename[:-3]  # Remove .md extension
                        prompts.append(
                            {
                                "name": prompt_name,
                                "description": description or title,
                            }
                        )

        return format_success_response({"prompts": prompts}, request_id)

    def _handle_prompts_get(self, request: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """处理获取提示词请求"""
        import os

        params = request.get("params", {})
        name = params.get("name")
        arguments = params.get("arguments", {})

        if not name:
            return format_error_response(-32602, "Prompt name is required", request_id)

        prompts_dir = os.path.join(os.path.dirname(__file__), "prompts")
        filepath = os.path.join(prompts_dir, f"{name}.md")

        if not os.path.exists(filepath):
            return format_error_response(-32602, f"Prompt not found: {name}", request_id)

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Format the prompt with any arguments
        try:
            formatted_content = content.format(**arguments)
        except (KeyError, ValueError):
            formatted_content = content

        return format_success_response(
            {
                "description": "命理咨询提示词模板",
                "messages": [
                    {
                        "role": "user",
                        "content": {"type": "text", "text": formatted_content},
                    }
                ],
            },
            request_id,
        )


def main():
    """主函数"""
    try:
        server = MingliMCPServer()
        server.start()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.exception("Fatal error")
        sys.exit(1)


if __name__ == "__main__":
    main()
