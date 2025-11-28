#!/usr/bin/env python3
"""
命理MCP服务器主入口

支持多种命理系统（紫微斗数、八字、占星等）的MCP集成
支持多种传输方式（stdio、HTTP、WebSocket）

This is a thin entry point that imports from the mcp package.
"""

import sys

from config import config
from mcp import MingliMCPServer

logger = config.get_logger(__name__)


def main():
    """主函数"""
    try:
        server = MingliMCPServer()
        server.start()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception:
        logger.exception("Fatal error")
        sys.exit(1)


if __name__ == "__main__":
    main()
