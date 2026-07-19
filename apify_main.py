#!/usr/bin/env python3
"""Apify Actor entry: run the Mingli MCP server in Standby mode.

Reuses the existing HTTP transport (stateless Streamable HTTP at /mcp) and
charges one pay-per-event unit per successful tools/call so the Actor can be
monetized with Apify's pay-per-event pricing model.

Also runs outside Apify (no `apify` SDK installed): charging becomes a no-op
and the server simply serves HTTP on ACTOR_WEB_SERVER_PORT / HTTP_PORT.
"""

import asyncio
import logging
import os

# 必须在导入 mingli_mcp 之前设置：config 在 import 时读取环境变量
os.environ.setdefault("TRANSPORT_TYPE", "http")
os.environ["HTTP_PORT"] = (
    os.getenv("ACTOR_WEB_SERVER_PORT")
    or os.getenv("ACTOR_STANDBY_PORT")
    or os.getenv("HTTP_PORT", "8080")
)

import uvicorn  # noqa: E402

from mingli_mcp.config import config  # noqa: E402
from mingli_mcp.mcp_server import MingliMCPServer  # noqa: E402

logger = logging.getLogger("apify_main")

try:
    from apify import Actor

    APIFY_AVAILABLE = True
except ImportError:
    Actor = None  # type: ignore[assignment]
    APIFY_AVAILABLE = False

# 事件名需与 Apify Console 里 Pay-per-event 定价配置的事件一致
CHARGE_EVENT = "tool-call"


def _make_charging_handler(server: MingliMCPServer, loop: asyncio.AbstractEventLoop):
    """包装MCP消息处理器：每次成功的tools/call计费一个PPE事件"""
    original = server.handle_request

    def handler(message):
        response = original(message)
        try:
            if (
                APIFY_AVAILABLE
                and isinstance(message, dict)
                and message.get("method") == "tools/call"
                and isinstance(response, dict)
                and "error" not in response
            ):
                # handler跑在uvicorn线程池里，把异步计费调度回事件循环（尽力而为）
                asyncio.run_coroutine_threadsafe(Actor.charge(CHARGE_EVENT), loop)
        except Exception:
            logger.exception("Failed to charge PPE event")
        return response

    return handler


async def serve() -> None:
    server = MingliMCPServer()
    loop = asyncio.get_running_loop()
    server.transport.set_message_handler(_make_charging_handler(server, loop))

    uv_config = uvicorn.Config(
        server.transport.app, host="0.0.0.0", port=config.HTTP_PORT, log_level="info"
    )
    await uvicorn.Server(uv_config).serve()


async def main() -> None:
    if APIFY_AVAILABLE:
        async with Actor:
            await serve()
    else:
        logger.warning("apify SDK not installed; running without pay-per-event charging")
        await serve()


if __name__ == "__main__":
    asyncio.run(main())
