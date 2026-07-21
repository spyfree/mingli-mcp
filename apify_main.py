#!/usr/bin/env python3
"""Apify Actor entry: run the Mingli MCP server in Standby mode.

Reuses the existing HTTP transport (stateless Streamable HTTP at /mcp) and
charges one pay-per-event unit per successful tools/call so the Actor can be
monetized with Apify's pay-per-event pricing model.

The entrypoint fails closed when the `apify` SDK is unavailable so paid tool
results cannot be returned without a confirmed charge.
"""

import asyncio
import logging
import os
from typing import Awaitable, Callable, Optional, Protocol

# 必须在导入 mingli_mcp 之前设置：config 在 import 时读取环境变量
os.environ.setdefault("TRANSPORT_TYPE", "http")
actor_http_port = (
    os.getenv("ACTOR_WEB_SERVER_PORT")
    or os.getenv("ACTOR_STANDBY_PORT")
    or os.getenv("HTTP_PORT", "8080")
    or "8080"
)
os.environ["HTTP_PORT"] = actor_http_port

import uvicorn  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from starlette.concurrency import run_in_threadpool  # noqa: E402

from mingli_mcp.config import config  # noqa: E402
from mingli_mcp.mcp_server import MingliMCPServer  # noqa: E402
from mingli_mcp.utils.formatters import format_error_response  # noqa: E402

logger = logging.getLogger("apify_main")

try:
    from apify import Actor

    APIFY_AVAILABLE = True
except ImportError:
    Actor = None  # type: ignore[assignment]
    APIFY_AVAILABLE = False

# 事件名需与 Apify Console 里 Pay-per-event 定价配置的事件一致
CHARGE_EVENT = "tool-call"
APIFY_BROWSER_ORIGINS = ["https://console.apify.com", "https://apify.com"]


class ChargeResult(Protocol):
    """Fields consumed from an Apify pay-per-event charge response."""

    charged_count: int
    event_charge_limit_reached: bool


ChargeFunction = Callable[[str], Awaitable[ChargeResult]]


def _make_charging_handler(server: MingliMCPServer, charge: ChargeFunction):
    """包装MCP消息处理器：每次成功的tools/call计费一个PPE事件"""
    original = server.handle_request

    async def handler(message):
        response = await run_in_threadpool(original, message)
        if (
            isinstance(message, dict)
            and message.get("method") == "tools/call"
            and isinstance(response, dict)
            and "error" not in response
        ):
            try:
                charge_result = await charge(CHARGE_EVENT)
            except Exception:
                logger.exception("Failed to charge PPE event")
                return format_error_response(
                    -32603, "Unable to charge for tool call", message.get("id")
                )
            if getattr(charge_result, "charged_count", 0) != 1:
                limit_reached = getattr(charge_result, "event_charge_limit_reached", False)
                error_message = (
                    "Tool call charge limit reached"
                    if limit_reached
                    else "Tool call could not be charged"
                )
                logger.warning(error_message)
                return format_error_response(-32001, error_message, message.get("id"))
        return response

    return handler


def create_app(charge: Optional[ChargeFunction] = None) -> FastAPI:
    """Create the Apify Standby HTTP application."""
    server = MingliMCPServer(http_cors_origins=APIFY_BROWSER_ORIGINS)
    if charge is None:
        if not APIFY_AVAILABLE:
            raise RuntimeError("Apify SDK is required for pay-per-event charging")
        charge = Actor.charge
    server.transport.set_message_handler(_make_charging_handler(server, charge))
    return server.transport.app


async def serve() -> None:
    uv_config = uvicorn.Config(
        create_app(), host="0.0.0.0", port=config.HTTP_PORT, log_level="info"
    )
    await uvicorn.Server(uv_config).serve()


async def main() -> None:
    if not APIFY_AVAILABLE:
        raise RuntimeError("Apify SDK is required for pay-per-event charging")
    async with Actor:
        await serve()


if __name__ == "__main__":
    asyncio.run(main())
