"""
MCP (Model Context Protocol) package for Mingli fortune-telling server.

This package provides modular components for the MCP server:
- server: Core MCP server implementation
- protocol: MCP protocol handling
- tools: Tool definitions and handlers
"""

from mcp.protocol import ProtocolHandler
from mcp.server import MingliMCPServer
from mcp.tools import ToolRegistry

__all__ = ["MingliMCPServer", "ProtocolHandler", "ToolRegistry"]
