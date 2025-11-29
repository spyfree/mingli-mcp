"""
MCP Tools package.

This package contains tool definitions and handlers for the MCP server.
"""

from typing import Any, Callable, Dict, List, Optional

from mcp.tools.bazi_handlers import (
    handle_analyze_bazi_element,
    handle_get_bazi_chart,
    handle_get_bazi_fortune,
)
from mcp.tools.definitions import get_all_tool_definitions
from mcp.tools.ziwei_handlers import (
    handle_analyze_ziwei_palace,
    handle_get_ziwei_chart,
    handle_get_ziwei_fortune,
)


class ToolRegistry:
    """Registry for MCP tools"""

    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._definitions: List[Dict[str, Any]] = []
        self._register_default_tools()

    def _register_default_tools(self):
        """Register all default tools"""
        # Ziwei tools
        self.register("get_ziwei_chart", handle_get_ziwei_chart)
        self.register("get_ziwei_fortune", handle_get_ziwei_fortune)
        self.register("analyze_ziwei_palace", handle_analyze_ziwei_palace)

        # Bazi tools
        self.register("get_bazi_chart", handle_get_bazi_chart)
        self.register("get_bazi_fortune", handle_get_bazi_fortune)
        self.register("analyze_bazi_element", handle_analyze_bazi_element)

        # System tools
        self.register("list_fortune_systems", self._handle_list_systems)

        # Load definitions
        self._definitions = get_all_tool_definitions()

    def register(self, name: str, handler: Callable) -> None:
        """Register a tool with its handler"""
        self._tools[name] = handler

    def get_handler(self, name: str) -> Optional[Callable]:
        """Get handler for a tool"""
        return self._tools.get(name)

    def get_definitions(self) -> List[Dict[str, Any]]:
        """Get all tool definitions for tools/list"""
        return self._definitions

    def _handle_list_systems(self, args: Dict[str, Any]) -> str:
        """工具：列出所有命理系统"""
        from systems import get_system, list_systems

        systems = list_systems()
        detailed = bool(args.get("detailed", False))

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

                if detailed and hasattr(system, "get_supported_palaces"):
                    palaces = system.get_supported_palaces()
                    if palaces:
                        result += f"- **支持宫位**: {', '.join(palaces)}\n"

                result += "\n"
            except Exception as e:
                result += f"## {system_name}\n\n"
                result += f"- **状态**: 加载失败 - {str(e)}\n\n"

        return result


__all__ = ["ToolRegistry", "get_all_tool_definitions"]
