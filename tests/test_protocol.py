"""
MCP Protocol handler tests.

Tests for initialize, tools/list, prompts/list, resources/list protocol methods.
Requirements: 2.1
"""

import pytest

from mcp.protocol import ProtocolHandler


class TestProtocolHandlerInitialize:
    """Tests for initialize protocol method."""

    @pytest.fixture
    def handler(self):
        """Create a ProtocolHandler instance."""
        return ProtocolHandler()

    def test_initialize_returns_protocol_version(self, handler):
        """Initialize should return the protocol version."""
        request = {"params": {"clientInfo": {"name": "test-client"}}}
        response = handler.handle_initialize(request, request_id=1)

        assert "result" in response
        assert "protocolVersion" in response["result"]
        assert response["result"]["protocolVersion"] == "2024-11-05"

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


class TestProtocolHandlerResourcesGet:
    """Tests for resources/get protocol method."""

    @pytest.fixture
    def handler(self):
        """Create a ProtocolHandler instance."""
        return ProtocolHandler()

    def test_resources_get_requires_uri(self, handler):
        """resources/get should return error when URI is missing."""
        request = {"params": {}}
        response = handler.handle_resources_get(request, request_id=1)

        assert "error" in response
        assert "URI is required" in response["error"]["message"]

    def test_resources_get_returns_error_for_unknown_uri(self, handler):
        """resources/get should return error for unknown URIs."""
        request = {"params": {"uri": "mingli://unknown-resource"}}
        response = handler.handle_resources_get(request, request_id=1)

        assert "error" in response
        assert "not found" in response["error"]["message"]

    def test_resources_get_returns_content_for_valid_uri(self, handler):
        """resources/get should return content for valid URIs."""
        request = {"params": {"uri": "mingli://configuration"}}
        response = handler.handle_resources_get(request, request_id=1)

        assert "result" in response
        assert "contents" in response["result"]
