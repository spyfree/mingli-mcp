"""
MCP Server tests.

Tests for server initialization and request routing.
Requirements: 2.1
"""

from unittest.mock import MagicMock, patch

import pytest

from mingli_mcp.mcp_server.protocol import ProtocolHandler
from mingli_mcp.mcp_server.server import MingliMCPServer
from mingli_mcp.mcp_server.tools import ToolRegistry


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

    def test_ignores_unknown_notifications(self, server):
        """Server must never respond to a notification (message without id)."""
        request = {"method": "notifications/cancelled", "params": {"requestId": 1}}

        response = server.handle_request(request)
        assert response is None


class TestModernStatelessProtocol:
    """Tests for the 2026-07-28 stateless protocol (per-request _meta)."""

    MODERN_META = {"io.modelcontextprotocol/protocolVersion": "2026-07-28"}

    @pytest.fixture
    def server(self):
        """Create a server instance with mocked transport."""
        with patch.object(MingliMCPServer, "_initialize_transport"):
            return MingliMCPServer()

    def test_routes_server_discover(self, server):
        """server/discover must be answered (spec: servers MUST implement it)."""
        request = {"method": "server/discover", "id": 1, "params": {"_meta": self.MODERN_META}}

        response = server.handle_request(request)
        assert response["result"]["supportedVersions"] == ["2026-07-28"]
        assert response["result"]["resultType"] == "complete"

    def test_modern_request_gets_decorated_result(self, server):
        """A request declaring 2026-07-28 in _meta gets resultType, serverInfo,
        and cache hints on list results."""
        request = {"method": "tools/list", "id": 2, "params": {"_meta": self.MODERN_META}}

        response = server.handle_request(request)
        result = response["result"]
        assert result["resultType"] == "complete"
        assert "io.modelcontextprotocol/serverInfo" in result["_meta"]
        assert result["ttlMs"] > 0
        assert result["cacheScope"] == "public"

    def test_modern_tool_call_has_result_type_but_no_cache_hints(self, server):
        """tools/call results carry resultType but are not cacheable."""
        request = {
            "method": "tools/call",
            "id": 3,
            "params": {
                "name": "list_fortune_systems",
                "arguments": {},
                "_meta": self.MODERN_META,
            },
        }

        response = server.handle_request(request)
        assert response["result"]["resultType"] == "complete"
        assert "ttlMs" not in response["result"]

    def test_legacy_request_response_is_unchanged(self, server):
        """Requests without _meta protocolVersion (legacy clients) must get
        byte-identical responses to previous releases: no new fields."""
        request = {"method": "tools/list", "id": 4}

        response = server.handle_request(request)
        assert "resultType" not in response["result"]
        assert "_meta" not in response["result"]
        assert "ttlMs" not in response["result"]

    def test_unsupported_meta_version_rejected_with_32022(self, server):
        """Declaring an unsupported version must return
        UnsupportedProtocolVersionError (-32022) with the supported list."""
        request = {
            "method": "tools/list",
            "id": 5,
            "params": {"_meta": {"io.modelcontextprotocol/protocolVersion": "1900-01-01"}},
        }

        response = server.handle_request(request)
        assert response["error"]["code"] == -32022
        assert "2026-07-28" in response["error"]["data"]["supported"]
        assert response["error"]["data"]["requested"] == "1900-01-01"

    def test_unsupported_meta_version_notification_gets_no_response(self, server):
        """Notifications are never answered, even when their version is bad."""
        request = {
            "method": "notifications/cancelled",
            "params": {"_meta": {"io.modelcontextprotocol/protocolVersion": "1900-01-01"}},
        }

        assert server.handle_request(request) is None

    def test_responds_to_ping(self, server):
        """Server should answer ping with an empty result."""
        request = {"method": "ping", "id": 7}

        response = server.handle_request(request)
        assert response["result"] == {}
        assert response["id"] == 7

    def test_routes_resources_read_request(self, server):
        """Server should route the standard resources/read method."""
        request = {
            "method": "resources/read",
            "id": 8,
            "params": {"uri": "mingli://configuration"},
        }

        response = server.handle_request(request)
        assert "result" in response
        assert response["result"]["contents"][0]["uri"] == "mingli://configuration"

    def test_routes_legacy_resources_get_request(self, server):
        """Server should keep accepting the legacy resources/get method."""
        request = {
            "method": "resources/get",
            "id": 9,
            "params": {"uri": "mingli://configuration"},
        }

        response = server.handle_request(request)
        assert "result" in response

    def test_resources_templates_list_returns_empty(self, server):
        """resources/templates/list should return an empty list, not an error."""
        request = {"method": "resources/templates/list", "id": 10}

        response = server.handle_request(request)
        assert response["result"] == {"resourceTemplates": []}


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

    def test_system_discovery_lists_only_implemented_capabilities(self, server):
        """Discovery must not advertise placeholders or hide implemented fortune tools."""
        request = {
            "method": "tools/call",
            "id": 11,
            "params": {"name": "list_fortune_systems", "arguments": {}},
        }

        text = server.handle_request(request)["result"]["content"][0]["text"]

        assert "## astrology" not in text
        assert "加载失败" not in text
        assert text.count("fortune: ✅") == 2

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
