"""
命理MCP服务器命令行入口

支持多种命理系统（紫微斗数、八字、占星等）的MCP集成
支持多种传输方式（stdio、HTTP）
"""

import sys

from mingli_mcp.config import config
from mingli_mcp.mcp_server import MingliMCPServer

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
