"""
MCP Server tests.

Tests for server initialization and request routing.
Requirements: 2.1
"""

from unittest.mock import MagicMock, patch

import pytest

from mcp.protocol import ProtocolHandler
from mcp.server import MingliMCPServer
from mcp.tools import ToolRegistry


class TestMingliMCPServerInitialization:
    """Tests for MCP server initialization."""

    def test_server_creates_protocol_handler(self):
        """Server should create a ProtocolHandler instance."""
        with patch.object(MingliMCPServer, "_initialize_transport"):
            server = MingliMCPServer()
            assert isinstance(server.protocol_handler, ProtocolHandler)

    def test_server_creates_tool_registry(self):
        """Server should create a ToolRegistry instance."""
        with patch.object(MingliMCPServer, "_initialize_transport"):
            server = MingliMCPServer()
            assert isinstance(server.tool_registry, ToolRegistry)

    def test_server_initializes_transport_on_creation(self):
        """Server should initialize transport during __init__."""
        with patch.object(MingliMCPServer, "_initialize_transport") as mock_init:
            MingliMCPServer()
            mock_init.assert_called_once()


class TestMingliMCPServerRequestRouting:
    """Tests for MCP server request routing."""

    @pytest.fixture
    def server(self):
        """Create a server instance with mocked transport."""
        with patch.object(MingliMCPServer, "_initialize_transport"):
            return MingliMCPServer()

    def test_routes_initialize_request(self, server):
        """Server should route initialize requests to protocol handler."""
        request = {"method": "initialize", "id": 1, "params": {}}

        with patch.object(server.protocol_handler, "handle_initialize") as mock:
            mock.return_value = {"jsonrpc": "2.0", "result": {}, "id": 1}
            server.handle_request(request)
            mock.assert_called_once_with(request, 1)

    def test_routes_tools_list_request(self, server):
        """Server should route tools/list requests to protocol handler."""
        request = {"method": "tools/list", "id": 2}

        with patch.object(server.protocol_handler, "handle_tools_list") as mock:
            mock.return_value = {"jsonrpc": "2.0", "result": {"tools": []}, "id": 2}
            server.handle_request(request)
            mock.assert_called_once()

    def test_routes_prompts_list_request(self, server):
        """Server should route prompts/list requests to protocol handler."""
        request = {"method": "prompts/list", "id": 3}

        with patch.object(server.protocol_handler, "handle_prompts_list") as mock:
            mock.return_value = {"jsonrpc": "2.0", "result": {"prompts": []}, "id": 3}
            server.handle_request(request)
            mock.assert_called_once_with(3)

    def test_routes_resources_list_request(self, server):
        """Server should route resources/list requests to protocol handler."""
        request = {"method": "resources/list", "id": 4}

        with patch.object(server.protocol_handler, "handle_resources_list") as mock:
            mock.return_value = {"jsonrpc": "2.0", "result": {"resources": []}, "id": 4}
            server.handle_request(request)
            mock.assert_called_once_with(4)

    def test_routes_tools_call_request(self, server):
        """Server should route tools/call requests to _handle_tools_call."""
        request = {
            "method": "tools/call",
            "id": 5,
            "params": {"name": "list_fortune_systems", "arguments": {}},
        }

        response = server.handle_request(request)
        assert "result" in response or "error" in response

    def test_returns_error_for_unknown_method(self, server):
        """Server should return error for unknown methods."""
        request = {"method": "unknown/method", "id": 6}

        response = server.handle_request(request)
        assert "error" in response
        assert response["error"]["code"] == -32601
        assert "Method not found" in response["error"]["message"]

    def test_handles_notifications_initialized(self, server):
        """Server should handle notifications/initialized without response."""
        request = {"method": "notifications/initialized"}

        response = server.handle_request(request)
        assert response is None


class TestMingliMCPServerToolsCall:
    """Tests for MCP server tools/call handling."""

    @pytest.fixture
    def server(self):
        """Create a server instance with mocked transport."""
        with patch.object(MingliMCPServer, "_initialize_transport"):
            return MingliMCPServer()

    def test_calls_registered_tool_handler(self, server):
        """Server should call the registered handler for a tool."""
        request = {
            "method": "tools/call",
            "id": 1,
            "params": {"name": "list_fortune_systems", "arguments": {}},
        }

        response = server.handle_request(request)
        assert "result" in response
        assert "content" in response["result"]

    def test_returns_error_for_unknown_tool(self, server):
        """Server should return error for unknown tools."""
        request = {
            "method": "tools/call",
            "id": 2,
            "params": {"name": "unknown_tool", "arguments": {}},
        }

        response = server.handle_request(request)
        assert "error" in response
        assert "Unknown tool" in response["error"]["message"]

    def test_returns_error_for_validation_failure(self, server):
        """Server should return error when tool validation fails."""
        request = {
            "method": "tools/call",
            "id": 3,
            "params": {"name": "get_ziwei_chart", "arguments": {}},  # Missing required params
        }

        response = server.handle_request(request)
        assert "error" in response
        assert response["error"]["code"] == -32602
