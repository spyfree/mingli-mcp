"""Apify Standby billing behavior through the public MCP HTTP endpoint."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from threading import Event

import pytest
from fastapi.testclient import TestClient

import apify_main


@dataclass
class FakeChargeResult:
    """Minimal representation of the Apify SDK charge result."""

    charged_count: int
    event_charge_limit_reached: bool = False


def _create_client(monkeypatch, charge):
    monkeypatch.setattr(apify_main.config, "TRANSPORT_TYPE", "http")
    monkeypatch.setattr(apify_main.config, "ENABLE_RATE_LIMIT", False)
    return TestClient(apify_main.create_app(charge=charge))


def _tool_call():
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "list_fortune_systems", "arguments": {}},
    }


def test_successful_tool_call_waits_for_charge_before_responding(monkeypatch):
    """A paid tool result must not be returned before its charge completes."""
    charge_started = Event()
    release_charge = Event()
    charged_events = []

    async def charge(event_name):
        charged_events.append(event_name)
        charge_started.set()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, release_charge.wait)
        return FakeChargeResult(charged_count=1)

    client = _create_client(monkeypatch, charge)

    with ThreadPoolExecutor(max_workers=1) as executor:
        pending_response = executor.submit(client.post, "/mcp", json=_tool_call())
        try:
            assert charge_started.wait(timeout=2)
            assert not pending_response.done()
        finally:
            release_charge.set()
        response = pending_response.result(timeout=2)

    assert response.status_code == 200
    assert "result" in response.json()
    assert charged_events == ["tool-call"]


def test_unpaid_tool_call_returns_charge_limit_error(monkeypatch):
    """A tool result must be withheld when no event could be charged."""

    async def charge(_event_name):
        return FakeChargeResult(charged_count=0, event_charge_limit_reached=True)

    response = _create_client(monkeypatch, charge).post("/mcp", json=_tool_call())

    assert response.status_code == 200
    assert response.json() == {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {"code": -32001, "message": "Tool call charge limit reached"},
    }


def test_charge_failure_returns_stable_mcp_error(monkeypatch):
    """An Apify API failure must not leak a paid tool result or exception details."""

    async def charge(_event_name):
        raise ConnectionError("sensitive upstream details")

    response = _create_client(monkeypatch, charge).post("/mcp", json=_tool_call())

    assert response.status_code == 200
    assert response.json() == {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {"code": -32603, "message": "Unable to charge for tool call"},
    }


def test_last_affordable_tool_call_still_returns_its_paid_result(monkeypatch):
    """Limit reached after this charge must not discard the result just paid for."""

    async def charge(_event_name):
        return FakeChargeResult(charged_count=1, event_charge_limit_reached=True)

    response = _create_client(monkeypatch, charge).post("/mcp", json=_tool_call())

    assert response.status_code == 200
    assert "result" in response.json()


def test_non_tool_request_does_not_create_a_charge(monkeypatch):
    """MCP discovery remains free and must not create a PPE event."""
    charged_events = []

    async def charge(event_name):
        charged_events.append(event_name)
        return FakeChargeResult(charged_count=1)

    response = _create_client(monkeypatch, charge).post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
    )

    assert response.status_code == 200
    assert "result" in response.json()
    assert charged_events == []


def test_failed_tool_call_does_not_create_a_charge(monkeypatch):
    """Invalid or failed tool calls remain errors and must not be billed."""
    charged_events = []

    async def charge(event_name):
        charged_events.append(event_name)
        return FakeChargeResult(charged_count=1)

    request = _tool_call()
    request["params"]["name"] = "unknown_tool"
    response = _create_client(monkeypatch, charge).post("/mcp", json=request)

    assert response.status_code == 200
    assert response.json()["error"]["code"] == -32602
    assert charged_events == []


def test_registered_tool_execution_error_does_not_create_a_charge(monkeypatch):
    """A registered tool that fails during execution must not be billed."""
    charged_events = []

    async def charge(event_name):
        charged_events.append(event_name)
        return FakeChargeResult(charged_count=1)

    request = _tool_call()
    request["params"] = {"name": "get_ziwei_chart", "arguments": {}}
    response = _create_client(monkeypatch, charge).post("/mcp", json=request)

    assert response.status_code == 200
    assert response.json()["error"]["code"] == -32602
    assert charged_events == []


def test_unconfigured_pricing_does_not_return_an_unpaid_result(monkeypatch):
    """A zero charge without a limit signal is still an unpaid call."""

    async def charge(_event_name):
        return FakeChargeResult(charged_count=0, event_charge_limit_reached=False)

    response = _create_client(monkeypatch, charge).post("/mcp", json=_tool_call())

    assert response.status_code == 200
    assert response.json() == {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {"code": -32001, "message": "Tool call could not be charged"},
    }


def test_missing_apify_sdk_fails_closed(monkeypatch):
    """The paid entrypoint must not silently serve results without the SDK."""
    monkeypatch.setattr(apify_main.config, "TRANSPORT_TYPE", "http")
    monkeypatch.setattr(apify_main.config, "ENABLE_RATE_LIMIT", False)
    monkeypatch.setattr(apify_main, "APIFY_AVAILABLE", False)

    with pytest.raises(RuntimeError, match="Apify SDK is required"):
        apify_main.create_app()
