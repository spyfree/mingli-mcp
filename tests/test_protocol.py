"""
MCP Protocol handler tests.

Tests for initialize, tools/list, prompts/list, resources/list protocol methods.
Requirements: 2.1
"""

import pytest

from mingli_mcp.mcp_server.protocol import ProtocolHandler
from mingli_mcp.mcp_server.tools.definitions import get_all_tool_definitions


class TestProtocolHandlerInitialize:
    """Tests for initialize protocol method."""

    @pytest.fixture
    def handler(self):
        """Create a ProtocolHandler instance."""
        return ProtocolHandler()

    def test_initialize_returns_latest_legacy_version_by_default(self, handler):
        """Initialize is the legacy-era handshake: without a requested version
        it should return the latest legacy (pre-2026-07-28) protocol version."""
        request = {"params": {"clientInfo": {"name": "test-client"}}}
        response = handler.handle_initialize(request, request_id=1)

        assert "result" in response
        assert (
            response["result"]["protocolVersion"] == ProtocolHandler.LATEST_LEGACY_PROTOCOL_VERSION
        )

    def test_initialize_echoes_supported_client_version(self, handler):
        """Initialize should echo the client's requested version if supported."""
        request = {"params": {"protocolVersion": "2024-11-05"}}
        response = handler.handle_initialize(request, request_id=1)

        assert response["result"]["protocolVersion"] == "2024-11-05"

    def test_initialize_falls_back_for_unsupported_version(self, handler):
        """Initialize should fall back to the latest legacy version
        when the client requests an unsupported one."""
        request = {"params": {"protocolVersion": "1999-01-01"}}
        response = handler.handle_initialize(request, request_id=1)

        assert (
            response["result"]["protocolVersion"] == ProtocolHandler.LATEST_LEGACY_PROTOCOL_VERSION
        )

    def test_initialize_does_not_negotiate_modern_versions(self, handler):
        """Modern (2026-07-28+) versions have no initialize handshake, so a client
        asking for one via initialize gets the latest legacy version instead."""
        request = {"params": {"protocolVersion": "2026-07-28"}}
        response = handler.handle_initialize(request, request_id=1)

        assert (
            response["result"]["protocolVersion"] == ProtocolHandler.LATEST_LEGACY_PROTOCOL_VERSION
        )

    def test_initialize_returns_server_info(self, handler):
        """Initialize should return server info."""
        request = {"params": {}}
        response = handler.handle_initialize(request, request_id=1)

        assert "serverInfo" in response["result"]
        assert "name" in response["result"]["serverInfo"]
        assert "version" in response["result"]["serverInfo"]

    def test_initialize_returns_capabilities(self, handler):
        """Initialize should return server capabilities."""
        request = {"params": {}}
        response = handler.handle_initialize(request, request_id=1)

        assert "capabilities" in response["result"]
        capabilities = response["result"]["capabilities"]
        assert "tools" in capabilities
        assert "prompts" in capabilities
        assert "resources" in capabilities

    def test_initialize_includes_request_id(self, handler):
        """Initialize response should include the request ID."""
        request = {"params": {}}
        response = handler.handle_initialize(request, request_id=42)

        assert response["id"] == 42

    def test_initialize_gives_client_user_centered_instructions(self, handler):
        """Server instructions should help an AI collect inputs and label results clearly."""
        response = handler.handle_initialize({"params": {}}, request_id=1)
        instructions = response["result"]["instructions"]

        assert "出生日期" in instructions
        assert "本命生肖" in instructions
        assert "流年生肖" in instructions
        assert "LOG_LEVEL" not in instructions


class TestProtocolHandlerToolsList:
    """Tests for tools/list protocol method."""

    @pytest.fixture
    def handler(self):
        """Create a ProtocolHandler instance."""
        return ProtocolHandler()

    def test_tools_list_returns_tools_array(self, handler):
        """tools/list should return an array of tools."""
        tool_definitions = [{"name": "test_tool", "description": "A test tool"}]
        response = handler.handle_tools_list(request_id=1, tool_definitions=tool_definitions)

        assert "result" in response
        assert "tools" in response["result"]
        assert isinstance(response["result"]["tools"], list)

    def test_tools_list_includes_provided_definitions(self, handler):
        """tools/list should include the provided tool definitions."""
        tool_definitions = [
            {"name": "tool1", "description": "Tool 1"},
            {"name": "tool2", "description": "Tool 2"},
        ]
        response = handler.handle_tools_list(request_id=1, tool_definitions=tool_definitions)

        assert len(response["result"]["tools"]) == 2
        assert response["result"]["tools"][0]["name"] == "tool1"
        assert response["result"]["tools"][1]["name"] == "tool2"

    def test_tools_list_includes_request_id(self, handler):
        """tools/list response should include the request ID."""
        response = handler.handle_tools_list(request_id=99, tool_definitions=[])

        assert response["id"] == 99

    def test_all_tools_expose_safe_model_hints_and_closed_schemas(self, handler):
        """Mainstream clients should receive complete, conservative tool metadata."""
        tools = get_all_tool_definitions()
        response = handler.handle_tools_list(request_id=1, tool_definitions=tools)

        for tool in response["result"]["tools"]:
            assert tool["title"]
            assert tool["inputSchema"]["additionalProperties"] is False
            assert tool["annotations"] == {
                "readOnlyHint": True,
                "destructiveHint": False,
                "idempotentHint": True,
                "openWorldHint": False,
            }


class TestProtocolHandlerPromptsList:
    """Tests for prompts/list protocol method."""

    @pytest.fixture
    def handler(self):
        """Create a ProtocolHandler instance."""
        return ProtocolHandler()

    def test_prompts_list_returns_prompts_array(self, handler):
        """prompts/list should return an array of prompts."""
        response = handler.handle_prompts_list(request_id=1)

        assert "result" in response
        assert "prompts" in response["result"]
        assert isinstance(response["result"]["prompts"], list)

    def test_prompts_list_includes_request_id(self, handler):
        """prompts/list response should include the request ID."""
        response = handler.handle_prompts_list(request_id=77)

        assert response["id"] == 77


class TestProtocolHandlerResourcesList:
    """Tests for resources/list protocol method."""

    @pytest.fixture
    def handler(self):
        """Create a ProtocolHandler instance."""
        return ProtocolHandler()

    def test_resources_list_returns_resources_array(self, handler):
        """resources/list should return an array of resources."""
        response = handler.handle_resources_list(request_id=1)

        assert "result" in response
        assert "resources" in response["result"]
        assert isinstance(response["result"]["resources"], list)

    def test_resources_list_contains_expected_resources(self, handler):
        """resources/list should contain the expected resource URIs."""
        response = handler.handle_resources_list(request_id=1)

        resources = response["result"]["resources"]
        resource_uris = [r["uri"] for r in resources]

        # Check for some expected resources
        assert "mingli://configuration" in resource_uris
        assert "mingli://heavenly-stems" in resource_uris
        assert "mingli://five-elements" in resource_uris

    def test_resources_list_includes_request_id(self, handler):
        """resources/list response should include the request ID."""
        response = handler.handle_resources_list(request_id=55)

        assert response["id"] == 55

    def test_resources_have_required_fields(self, handler):
        """Each resource should have uri, name, and description."""
        response = handler.handle_resources_list(request_id=1)

        for resource in response["result"]["resources"]:
            assert "uri" in resource
            assert "name" in resource
            assert "description" in resource


class TestProtocolHandlerPromptsGet:
    """Tests for prompts/get protocol method."""

    @pytest.fixture
    def handler(self):
        """Create a ProtocolHandler instance."""
        return ProtocolHandler()

    def test_prompts_get_requires_name(self, handler):
        """prompts/get should return error when name is missing."""
        request = {"params": {}}
        response = handler.handle_prompts_get(request, request_id=1)

        assert "error" in response
        assert "name is required" in response["error"]["message"]

    def test_prompts_get_rejects_path_traversal(self, handler):
        """prompts/get should reject path traversal attempts."""
        request = {"params": {"name": "../etc/passwd"}}
        response = handler.handle_prompts_get(request, request_id=1)

        assert "error" in response
        assert "Invalid prompt" in response["error"]["message"]

    def test_prompts_get_rejects_dotted_names(self, handler):
        """prompts/get should reject names starting with dot."""
        request = {"params": {"name": ".hidden"}}
        response = handler.handle_prompts_get(request, request_id=1)

        assert "error" in response


class TestProtocolHandlerResourcesRead:
    """Tests for resources/read protocol method."""

    @pytest.fixture
    def handler(self):
        """Create a ProtocolHandler instance."""
        return ProtocolHandler()

    def test_resources_read_requires_uri(self, handler):
        """resources/read should return error when URI is missing."""
        request = {"params": {}}
        response = handler.handle_resources_read(request, request_id=1)

        assert "error" in response
        assert "URI is required" in response["error"]["message"]

    def test_resources_read_returns_error_for_unknown_uri(self, handler):
        """resources/read should return error for unknown URIs."""
        request = {"params": {"uri": "mingli://unknown-resource"}}
        response = handler.handle_resources_read(request, request_id=1)

        assert "error" in response
        assert "not found" in response["error"]["message"]

    def test_resources_read_returns_content_for_valid_uri(self, handler):
        """resources/read should return content for valid URIs."""
        request = {"params": {"uri": "mingli://configuration"}}
        response = handler.handle_resources_read(request, request_id=1)

        assert "result" in response
        assert "contents" in response["result"]

    def test_resources_read_contents_include_uri_and_mime_type(self, handler):
        """Each content item must carry uri and mimeType per the MCP spec."""
        request = {"params": {"uri": "mingli://configuration"}}
        response = handler.handle_resources_read(request, request_id=1)

        content = response["result"]["contents"][0]
        assert content["uri"] == "mingli://configuration"
        assert content["mimeType"] == "text/markdown"
        assert content["text"]

    def test_resources_get_alias_still_works(self, handler):
        """Legacy resources/get handler name should remain as an alias."""
        request = {"params": {"uri": "mingli://configuration"}}
        response = handler.handle_resources_get(request, request_id=1)

        assert "result" in response

    def test_resources_list_entries_include_mime_type(self, handler):
        """resources/list entries should declare their mimeType."""
        response = handler.handle_resources_list(request_id=1)

        for resource in response["result"]["resources"]:
            assert resource["mimeType"] == "text/markdown"


class TestProtocolHandlerServerDiscover:
    """Tests for the 2026-07-28 server/discover method (MUST be implemented)."""

    @pytest.fixture
    def handler(self):
        """Create a ProtocolHandler instance."""
        return ProtocolHandler()

    def test_discover_lists_only_modern_versions(self, handler):
        """supportedVersions advertises stateless (modern) versions only;
        legacy versions are negotiated through initialize instead."""
        response = handler.handle_server_discover({"params": {}}, request_id=1)

        assert response["result"]["supportedVersions"] == ["2026-07-28"]

    def test_discover_returns_capabilities_and_instructions(self, handler):
        """Discovery should expose the same capabilities and instructions
        as the legacy initialize handshake."""
        discover = handler.handle_server_discover({"params": {}}, request_id=1)
        initialize = handler.handle_initialize({"params": {}}, request_id=2)

        assert discover["result"]["capabilities"] == initialize["result"]["capabilities"]
        assert discover["result"]["instructions"] == initialize["result"]["instructions"]

    def test_discover_reports_server_info_in_meta(self, handler):
        """serverInfo travels in _meta per the final 2026-07-28 schema."""
        response = handler.handle_server_discover({"params": {}}, request_id=1)

        server_info = response["result"]["_meta"]["io.modelcontextprotocol/serverInfo"]
        assert server_info["name"]
        assert server_info["version"]

    def test_discover_result_is_cacheable_and_complete(self, handler):
        """DiscoverResult is a CacheableResult and carries resultType."""
        response = handler.handle_server_discover({"params": {}}, request_id=1)

        result = response["result"]
        assert result["resultType"] == "complete"
        assert isinstance(result["ttlMs"], int) and result["ttlMs"] > 0
        assert result["cacheScope"] in ("public", "private")

    def test_discover_works_without_meta(self, handler):
        """A bare probe without params/_meta must still get an answer
        (dual-era clients use it to detect the server's era on stdio)."""
        response = handler.handle_server_discover({}, request_id="probe-1")

        assert "result" in response
        assert response["id"] == "probe-1"


class TestModernResultDecoration:
    """Tests for decorate_modern_result (2026-07-28 per-request metadata)."""

    @pytest.fixture
    def handler(self):
        """Create a ProtocolHandler instance."""
        return ProtocolHandler()

    def test_adds_result_type_and_server_info(self, handler):
        """Every modern result must carry resultType; serverInfo rides in _meta."""
        response = handler.handle_tools_list(request_id=1, tool_definitions=[])
        handler.decorate_modern_result(response, "tools/list")

        result = response["result"]
        assert result["resultType"] == "complete"
        assert "io.modelcontextprotocol/serverInfo" in result["_meta"]

    def test_adds_cache_hints_to_list_results(self, handler):
        """tools/list, prompts/list, resources/list and resources/read
        results must carry ttlMs and cacheScope for modern clients."""
        for method, response in [
            ("tools/list", handler.handle_tools_list(request_id=1, tool_definitions=[])),
            ("prompts/list", handler.handle_prompts_list(request_id=1)),
            ("resources/list", handler.handle_resources_list(request_id=1)),
            (
                "resources/read",
                handler.handle_resources_read(
                    {"params": {"uri": "mingli://configuration"}}, request_id=1
                ),
            ),
        ]:
            handler.decorate_modern_result(response, method)
            assert response["result"]["ttlMs"] > 0, method
            assert response["result"]["cacheScope"] == "public", method

    def test_does_not_add_cache_hints_to_tool_calls(self, handler):
        """tools/call results are not CacheableResults."""
        from mingli_mcp.utils.formatters import format_success_response

        response = format_success_response({"content": []}, request_id=1)
        handler.decorate_modern_result(response, "tools/call")

        assert response["result"]["resultType"] == "complete"
        assert "ttlMs" not in response["result"]
        assert "cacheScope" not in response["result"]

    def test_leaves_error_responses_untouched(self, handler):
        """Error responses have no result object and must not be modified."""
        from mingli_mcp.utils.formatters import format_error_response

        response = format_error_response(-32601, "Method not found", request_id=1)
        original = dict(response["error"])
        handler.decorate_modern_result(response, "tools/list")

        assert response["error"] == original
        assert "result" not in response
