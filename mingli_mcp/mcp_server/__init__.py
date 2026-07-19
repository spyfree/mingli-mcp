"""
MCP (Model Context Protocol) package for Mingli fortune-telling server.

This package provides modular components for the MCP server:
- server: Core MCP server implementation
- protocol: MCP protocol handling
- tools: Tool definitions and handlers
"""

from mingli_mcp.mcp_server.protocol import ProtocolHandler
from mingli_mcp.mcp_server.server import MingliMCPServer
from mingli_mcp.mcp_server.tools import ToolRegistry

__all__ = ["MingliMCPServer", "ProtocolHandler", "ToolRegistry"]
