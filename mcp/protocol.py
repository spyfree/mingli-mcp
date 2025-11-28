"""
MCP Protocol handling.

This module contains the ProtocolHandler class that handles
MCP protocol methods like initialize, tools/list, prompts/list, etc.
"""

from pathlib import Path
from typing import Any, Dict, List

from config import config
from utils.formatters import format_error_response, format_success_response

logger = config.get_logger(__name__)


class ProtocolHandler:
    """Handles MCP protocol methods"""

    PROTOCOL_VERSION = "2024-11-05"

    def handle_initialize(self, request: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
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
                    "resources": {},
                },
                "instructions": "命理MCP服务提供紫微斗数、八字等中国传统命理系统的分析工具。所有配置都是可选的，服务器可以在没有任何配置的情况下运行。可通过环境变量自定义行为（LOG_LEVEL, TRANSPORT_TYPE, DEFAULT_LANGUAGE等），详见文档。",
            },
            request_id,
        )

    def handle_tools_list(
        self, request_id: Any, tool_definitions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """处理工具列表请求"""
        return format_success_response({"tools": tool_definitions}, request_id)

    def handle_prompts_list(self, request_id: Any) -> Dict[str, Any]:
        """处理提示词列表请求"""
        import os

        prompts_dir = Path(__file__).parent.parent / "prompts"
        prompts = []

        if prompts_dir.exists():
            for filename in os.listdir(prompts_dir):
                if filename.endswith(".md"):
                    filepath = prompts_dir / filename
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        lines = content.split("\n")
                        title = lines[0].replace("#", "").strip()
                        description = ""
                        for line in lines[1:]:
                            if line.strip() and not line.startswith("#"):
                                description = line.strip()
                                break

                        prompt_name = filename[:-3]
                        prompts.append(
                            {
                                "name": prompt_name,
                                "description": description or title,
                            }
                        )

        return format_success_response({"prompts": prompts}, request_id)

    def handle_prompts_get(self, request: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """处理获取提示词请求"""
        params = request.get("params", {})
        name = params.get("name")
        arguments = params.get("arguments", {})

        if not name:
            return format_error_response(-32602, "Prompt name is required", request_id)

        # Security: validate filename to prevent path traversal
        if "/" in name or "\\" in name or name.startswith(".") or ".." in name:
            logger.warning(f"Potential path traversal attempt: {name}")
            return format_error_response(-32602, "Invalid prompt name", request_id)

        prompts_dir = Path(__file__).parent.parent / "prompts"
        filepath = prompts_dir / f"{name}.md"

        # Ensure target file is within prompts directory
        try:
            filepath.resolve().relative_to(prompts_dir.resolve())
        except ValueError:
            logger.warning(f"Path traversal blocked: {filepath}")
            return format_error_response(-32602, "Invalid prompt path", request_id)

        if not filepath.exists():
            return format_error_response(-32602, f"Prompt not found: {name}", request_id)

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

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

    def handle_resources_list(self, request_id: Any) -> Dict[str, Any]:
        """处理资源列表请求"""
        resources = [
            {
                "uri": "mingli://configuration",
                "name": "服务器配置选项",
                "description": "可选的环境变量配置，用于自定义服务器行为（无配置也可正常运行）",
            },
            {
                "uri": "mingli://heavenly-stems",
                "name": "天干地支对照表",
                "description": "十天干十二地支的详细信息，包括五行属性、阴阳属性等",
            },
            {
                "uri": "mingli://five-elements",
                "name": "五行相生相克",
                "description": "五行（金木水火土）的相生相克关系和特性",
            },
            {
                "uri": "mingli://twelve-palaces",
                "name": "紫微十二宫位",
                "description": "紫微斗数十二宫位的名称、含义和主事",
            },
            {
                "uri": "mingli://ziwei-main-stars",
                "name": "紫微主星",
                "description": "紫微斗数十四主星的特性和影响",
            },
            {
                "uri": "mingli://time-periods",
                "name": "十二时辰对照表",
                "description": "十二时辰与现代表时间的对照关系",
            },
            {
                "uri": "mingli://fortune-terms",
                "name": "命理术语表",
                "description": "常用的命理术语及其含义解释",
            },
        ]

        return format_success_response({"resources": resources}, request_id)

    def handle_resources_get(self, request: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """处理获取资源请求"""
        from mcp.resources import get_resource_content

        params = request.get("params", {})
        uri = params.get("uri")

        if not uri:
            return format_error_response(-32602, "Resource URI is required", request_id)

        content = get_resource_content(uri)
        if content is None:
            return format_error_response(-32602, f"Resource not found: {uri}", request_id)

        return format_success_response(
            {
                "contents": [
                    {
                        "type": "text",
                        "text": content,
                    }
                ]
            },
            request_id,
        )
