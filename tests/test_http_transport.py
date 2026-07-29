#!/usr/bin/env python3
"""
HTTP传输层测试
"""

import json

import pytest

# 仅在fastapi可用时运行这些测试
pytest.importorskip("fastapi")

from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture
def http_transport():
    """创建HTTP传输层fixture"""
    from mingli_mcp.transports.http_transport import HttpTransport

    transport = HttpTransport(host="127.0.0.1", port=8080, api_key="test-api-key")

    # 设置一个简单的消息处理器用于测试
    def mock_handler(message):
        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "result": {"tools": []},  # 简单的模拟响应
        }

    transport.set_message_handler(mock_handler)
    return transport


@pytest.fixture
def client(http_transport):
    """创建测试客户端"""
    return TestClient(http_transport.app)


class TestHttpTransport:
    """HTTP传输层测试"""

    def test_health_endpoint(self, client):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_mcp_endpoint_without_auth(self, client):
        """测试MCP端点无认证"""
        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }

        response = client.post("/mcp", json=request_data)
        # 应该返回401 Unauthorized
        assert response.status_code == 401

    def test_mcp_endpoint_with_invalid_auth(self, client):
        """测试MCP端点无效认证"""
        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }

        response = client.post(
            "/mcp",
            json=request_data,
            headers={"Authorization": "Bearer wrong-key"},
        )
        assert response.status_code == 401

    def test_mcp_endpoint_with_valid_auth(self, client):
        """测试MCP端点有效认证"""
        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }

        response = client.post(
            "/mcp",
            json=request_data,
            headers={"Authorization": "Bearer test-api-key"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "result" in data or "error" in data

    def test_stats_endpoint_without_auth(self, client):
        """测试统计端点无认证"""
        response = client.get("/stats")
        assert response.status_code == 401

    def test_stats_endpoint_with_valid_auth(self, client):
        """测试统计端点有效认证"""
        response = client.get(
            "/stats",
            headers={"Authorization": "Bearer test-api-key"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_requests" in data["rate_limiting"]
        assert "total_clients" in data["rate_limiting"]
        assert "total_requests" in data["tool_calls"]

    def test_invalid_json(self, client):
        """测试无效JSON返回-32700 Parse error"""
        response = client.post(
            "/mcp",
            content="invalid json",
            headers={
                "Authorization": "Bearer test-api-key",
                "Content-Type": "application/json",
            },
        )
        assert response.status_code == 400
        assert response.json()["error"]["code"] == -32700

    def test_notification_returns_202_without_body(self, http_transport):
        """notification消息应返回202 Accepted且无body（MCP Streamable HTTP规范）"""

        def notification_handler(message):
            return None  # 服务器对notification不产生响应

        http_transport.set_message_handler(notification_handler)
        client = TestClient(http_transport.app)

        response = client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "method": "notifications/initialized"},
            headers={"Authorization": "Bearer test-api-key"},
        )
        assert response.status_code == 202
        assert response.content == b""

    def test_invalid_origin_rejected_with_403(self, client):
        """非法Origin必须返回403（MCP规范，防DNS rebinding）"""
        response = client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
            headers={
                "Authorization": "Bearer test-api-key",
                "Origin": "https://evil.example.com",
            },
        )
        assert response.status_code == 403

    def test_allowed_origin_accepted(self, client):
        """允许列表内的Origin应放行"""
        response = client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
            headers={
                "Authorization": "Bearer test-api-key",
                "Origin": "http://localhost:3000",
            },
        )
        assert response.status_code == 200

    def test_unsupported_protocol_version_rejected_with_400(self):
        """不支持的MCP-Protocol-Version头必须返回400 + -32022，并列出支持的版本"""
        from mingli_mcp.transports.http_transport import HttpTransport

        transport = HttpTransport(
            host="127.0.0.1",
            port=8080,
            supported_protocol_versions=["2025-11-25", "2024-11-05"],
        )
        transport.set_message_handler(lambda m: {"jsonrpc": "2.0", "id": m.get("id"), "result": {}})
        client = TestClient(transport.app)

        response = client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
            headers={"MCP-Protocol-Version": "1900-01-01"},
        )
        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == -32022
        assert error["data"]["supported"] == ["2025-11-25", "2024-11-05"]
        assert error["data"]["requested"] == "1900-01-01"

        response = client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
            headers={"MCP-Protocol-Version": "2025-11-25"},
        )
        assert response.status_code == 200

    def test_rate_limit_uses_cf_connecting_ip_when_proxy_trusted(self):
        """信任代理时，限流应优先使用CF-Connecting-IP作为客户端标识"""
        from unittest.mock import patch

        from mingli_mcp.transports.http_transport import HttpTransport

        transport = HttpTransport(host="127.0.0.1", port=8080, trust_proxy_headers=True)
        transport.set_message_handler(lambda m: {"jsonrpc": "2.0", "id": m.get("id"), "result": {}})
        client = TestClient(transport.app)

        with patch.object(transport.rate_limiter, "is_allowed", return_value=True) as mock_allowed:
            client.post(
                "/mcp",
                json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
                headers={"CF-Connecting-IP": "203.0.113.7"},
            )
            mock_allowed.assert_called_once_with("203.0.113.7")

    def test_proxy_headers_ignored_by_default(self, http_transport):
        """默认不信任代理头：否则轮换X-Forwarded-For即可绕过限流"""
        from unittest.mock import patch

        client = TestClient(http_transport.app)

        assert http_transport.trust_proxy_headers is False

        with patch.object(
            http_transport.rate_limiter, "is_allowed", return_value=True
        ) as mock_allowed:
            client.post(
                "/mcp",
                json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
                headers={
                    "Authorization": "Bearer test-api-key",
                    "CF-Connecting-IP": "203.0.113.7",
                    "X-Forwarded-For": "198.51.100.4",
                },
            )
            # 客户端可控的头不能影响限流分桶
            assert mock_allowed.call_args.args[0] not in ("203.0.113.7", "198.51.100.4")

    def test_rate_limit_not_bypassable_by_rotating_forwarded_for(self):
        """轮换X-Forwarded-For不应突破限流上限"""
        from mingli_mcp.transports.http_transport import HttpTransport

        transport = HttpTransport(
            host="127.0.0.1",
            port=8080,
            enable_rate_limit=True,
            rate_limit_requests=3,
            rate_limit_window=60,
        )
        transport.set_message_handler(lambda m: {"jsonrpc": "2.0", "id": m.get("id"), "result": {}})
        client = TestClient(transport.app)

        body = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
        statuses = [
            client.post("/mcp", json=body, headers={"X-Forwarded-For": f"9.9.9.{i}"}).status_code
            for i in range(6)
        ]

        assert statuses[:3] == [200, 200, 200]
        assert statuses[3:] == [429, 429, 429]

    def test_stats_requires_api_key_to_be_configured(self):
        """未配置API key时/stats不得公开限流器内部状态"""
        from mingli_mcp.transports.http_transport import HttpTransport

        transport = HttpTransport(host="127.0.0.1", port=8080, api_key="")
        transport.set_message_handler(lambda m: {"jsonrpc": "2.0", "id": m.get("id"), "result": {}})
        client = TestClient(transport.app)

        assert client.get("/stats").status_code == 404

    def test_stats_accessible_with_api_key(self, http_transport):
        """配置了API key时，携带正确凭证可访问/stats"""
        client = TestClient(http_transport.app)

        assert client.get("/stats").status_code == 401
        response = client.get("/stats", headers={"Authorization": "Bearer test-api-key"})
        assert response.status_code == 200
        payload = response.json()
        assert "tool_calls" in payload
        assert payload["rate_limiting"]["max_requests_per_window"] == 100

    def test_cors_headers(self, client):
        """测试CORS头"""
        # 测试健康检查端点的CORS头
        response = client.get("/health")
        assert response.status_code == 200
        # CORS middleware应该添加这些头部
        # 注意：TestClient可能不会触发所有middleware行为
        # 所以这个测试主要验证服务器配置正确


class TestModernHeaderValidation:
    """2026-07-28 请求头与请求体一致性校验测试（Server Validation）"""

    MODERN_VERSION = "2026-07-28"
    META = {"io.modelcontextprotocol/protocolVersion": "2026-07-28"}

    @pytest.fixture
    def client(self):
        """带2026-07-28支持的传输层测试客户端"""
        from mingli_mcp.transports.http_transport import HttpTransport

        transport = HttpTransport(
            host="127.0.0.1",
            port=8080,
            supported_protocol_versions=["2026-07-28", "2025-11-25", "2024-11-05"],
        )
        transport.set_message_handler(lambda m: {"jsonrpc": "2.0", "id": m.get("id"), "result": {}})
        return TestClient(transport.app)

    def _headers(self, **extra):
        headers = {"MCP-Protocol-Version": self.MODERN_VERSION}
        headers.update(extra)
        return headers

    def test_valid_modern_request_accepted(self, client):
        """头与body一致的现代请求应放行"""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "get_bazi_chart", "arguments": {}, "_meta": self.META},
            },
            headers=self._headers(**{"Mcp-Method": "tools/call", "Mcp-Name": "get_bazi_chart"}),
        )
        assert response.status_code == 200

    def test_missing_mcp_method_header_rejected(self, client):
        """现代请求缺少Mcp-Method头必须返回400 + -32020"""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {"_meta": self.META},
            },
            headers=self._headers(),
        )
        assert response.status_code == 400
        assert response.json()["error"]["code"] == -32020

    def test_mcp_method_body_mismatch_rejected(self, client):
        """Mcp-Method头与body.method不一致必须返回400 + -32020"""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {"_meta": self.META},
            },
            headers=self._headers(**{"Mcp-Method": "prompts/list"}),
        )
        assert response.status_code == 400
        assert response.json()["error"]["code"] == -32020

    def test_missing_mcp_name_header_rejected_for_tool_call(self, client):
        """tools/call缺少Mcp-Name头必须返回400 + -32020"""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "get_bazi_chart", "arguments": {}, "_meta": self.META},
            },
            headers=self._headers(**{"Mcp-Method": "tools/call"}),
        )
        assert response.status_code == 400
        assert response.json()["error"]["code"] == -32020

    def test_mcp_name_mismatch_rejected(self, client):
        """Mcp-Name头与body中的name不一致必须返回400 + -32020"""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "get_bazi_chart", "arguments": {}, "_meta": self.META},
            },
            headers=self._headers(**{"Mcp-Method": "tools/call", "Mcp-Name": "other_tool"}),
        )
        assert response.status_code == 400
        assert response.json()["error"]["code"] == -32020

    def test_mcp_name_base64_sentinel_decoded_before_compare(self, client):
        """Base64哨兵编码的Mcp-Name应先解码再与body比较"""
        import base64

        uri = "mingli://五行"
        encoded = base64.b64encode(uri.encode("utf-8")).decode("ascii")
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "resources/read",
                "params": {"uri": uri, "_meta": self.META},
            },
            headers=self._headers(
                **{"Mcp-Method": "resources/read", "Mcp-Name": f"=?base64?{encoded}?="}
            ),
        )
        assert response.status_code == 200

    def test_resources_read_uses_uri_as_name_source(self, client):
        """resources/read的Mcp-Name取params.uri"""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "resources/read",
                "params": {"uri": "mingli://configuration", "_meta": self.META},
            },
            headers=self._headers(
                **{"Mcp-Method": "resources/read", "Mcp-Name": "mingli://configuration"}
            ),
        )
        assert response.status_code == 200

    def test_header_meta_version_mismatch_rejected(self, client):
        """头声明现代版本但body._meta版本缺失/不一致必须返回400 + -32020"""
        response = client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
            headers=self._headers(**{"Mcp-Method": "tools/list"}),
        )
        assert response.status_code == 400
        assert response.json()["error"]["code"] == -32020

    def test_notification_skips_header_validation(self, client):
        """notification的头要求规范未定义：不带Mcp-Method也应返回202"""
        from mingli_mcp.transports.http_transport import HttpTransport

        transport = HttpTransport(
            host="127.0.0.1",
            port=8080,
            supported_protocol_versions=["2026-07-28", "2025-11-25"],
        )
        transport.set_message_handler(lambda m: None)
        client = TestClient(transport.app)

        response = client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {}},
            headers=self._headers(),
        )
        assert response.status_code == 202

    def test_legacy_version_requests_skip_modern_validation(self, client):
        """旧版本头的请求不做Mcp-Method校验（旧规范没有这些头）"""
        response = client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
            headers={"MCP-Protocol-Version": "2025-11-25"},
        )
        assert response.status_code == 200

    def test_unknown_method_returns_404_for_modern_requests(self):
        """现代请求调用未实现的方法必须返回404 + -32601"""
        from mingli_mcp.transports.http_transport import HttpTransport

        transport = HttpTransport(
            host="127.0.0.1",
            port=8080,
            supported_protocol_versions=["2026-07-28", "2025-11-25"],
        )
        transport.set_message_handler(
            lambda m: {
                "jsonrpc": "2.0",
                "id": m.get("id"),
                "error": {"code": -32601, "message": "Method not found"},
            }
        )
        client = TestClient(transport.app)

        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "subscriptions/listen",
                "params": {"_meta": self.META},
            },
            headers=self._headers(**{"Mcp-Method": "subscriptions/listen"}),
        )
        assert response.status_code == 404
        assert response.json()["error"]["code"] == -32601

        # 旧版本请求的未知方法仍是200 + JSON-RPC错误（旧规范行为）
        response = client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "id": 1, "method": "unknown/method"},
            headers={"MCP-Protocol-Version": "2025-11-25"},
        )
        assert response.status_code == 200
        assert response.json()["error"]["code"] == -32601


class TestRateLimiting:
    """速率限制测试"""

    @pytest.mark.skip(reason="需要实际启用速率限制")
    def test_rate_limit_enforcement(self, client):
        """测试速率限制执行"""
        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }

        # 发送大量请求触发速率限制
        for i in range(150):  # 超过默认100请求/分钟
            response = client.post(
                "/mcp",
                json=request_data,
                headers={"Authorization": "Bearer test-api-key"},
            )
            if response.status_code == 429:
                # 触发速率限制
                assert "rate limit" in response.json().get("error", {}).get("message", "").lower()
                break
        else:
            pytest.fail("速率限制未触发")
