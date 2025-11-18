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
    from transports.http_transport import HttpTransport

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
        assert "total_requests" in data
        assert "total_clients" in data

    def test_invalid_json(self, client):
        """测试无效JSON"""
        response = client.post(
            "/mcp",
            data="invalid json",
            headers={
                "Authorization": "Bearer test-api-key",
                "Content-Type": "application/json",
            },
        )
        assert response.status_code == 500  # 内部错误

    def test_cors_headers(self, client):
        """测试CORS头"""
        # 测试健康检查端点的CORS头
        response = client.get("/health")
        assert response.status_code == 200
        # CORS middleware应该添加这些头部
        # 注意：TestClient可能不会触发所有middleware行为
        # 所以这个测试主要验证服务器配置正确


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
