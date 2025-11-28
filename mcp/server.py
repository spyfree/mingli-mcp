"""
MCP Server core implementation.

This module contains the main MingliMCPServer class that coordinates
protocol handling, tool execution, and transport management.
"""

from typing import Any, Dict

from config import config
from core.exceptions import (
    SystemError,
    SystemNotFoundError,
    ToolCallError,
    ValidationError,
)
from mcp.protocol import ProtocolHandler
from mcp.tools import ToolRegistry
from transports import StdioTransport
from utils.formatters import format_error_response

logger = config.get_logger(__name__)


class MingliMCPServer:
    """命理MCP服务器"""

    def __init__(self):
        self.transport = None
        self.protocol_handler = ProtocolHandler()
        self.tool_registry = ToolRegistry()
        self._initialize_transport()

    def _initialize_transport(self):
        """初始化传输层"""
        from transports import HTTP_TRANSPORT_AVAILABLE

        transport_type = config.TRANSPORT_TYPE.lower()

        if transport_type == "stdio":
            self.transport = StdioTransport()
        elif transport_type == "http":
            if not HTTP_TRANSPORT_AVAILABLE:
                raise ImportError(
                    "HTTP transport is not available. Please install mingli-mcp with HTTP support:\n"
                    "  pip install mingli-mcp[http]\n"
                    "or\n"
                    "  pip install mingli-mcp (which includes all dependencies)"
                )
            from transports import HttpTransport

            self.transport = HttpTransport(
                host=config.HTTP_HOST, port=config.HTTP_PORT, api_key=config.HTTP_API_KEY
            )
        else:
            raise ValueError(f"Unsupported transport type: {transport_type}")

        self.transport.set_message_handler(self.handle_request)
        logger.info(f"Initialized {transport_type} transport")

    def start(self):
        """启动MCP服务器"""
        from systems import list_systems

        logger.info(f"Starting {config.MCP_SERVER_NAME} v{config.MCP_SERVER_VERSION}")
        logger.info(f"Available systems: {', '.join(list_systems())}")
        self.transport.start()

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理MCP请求

        Args:
            request: JSON-RPC请求

        Returns:
            JSON-RPC响应
        """
        method = request.get("method")
        request_id = request.get("id")

        try:
            # Protocol methods
            if method == "initialize":
                return self.protocol_handler.handle_initialize(request, request_id)
            elif method == "notifications/initialized":
                logger.info("Received initialized notification")
                return None
            elif method == "tools/list":
                return self.protocol_handler.handle_tools_list(
                    request_id, self.tool_registry.get_definitions()
                )
            elif method == "tools/call":
                return self._handle_tools_call(request, request_id)
            elif method == "prompts/list":
                return self.protocol_handler.handle_prompts_list(request_id)
            elif method == "prompts/get":
                return self.protocol_handler.handle_prompts_get(request, request_id)
            elif method == "resources/list":
                return self.protocol_handler.handle_resources_list(request_id)
            elif method == "resources/get":
                return self.protocol_handler.handle_resources_get(request, request_id)
            else:
                logger.warning(f"Unknown method: {method}")
                return format_error_response(-32601, f"Method not found: {method}", request_id)

        except (ValidationError, SystemNotFoundError) as e:
            logger.error(f"Request validation error for {method}: {e}")
            return format_error_response(-32602, str(e), request_id)
        except Exception as e:
            logger.exception(f"Unexpected error handling request: {method}")
            return format_error_response(-32603, f"Internal error: {str(e)}", request_id)

    def _handle_tools_call(self, request: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """处理工具调用请求"""
        from utils.formatters import format_success_response

        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        logger.info(f"Tool call: {tool_name}")
        logger.debug(f"Arguments: {arguments}")

        try:
            handler = self.tool_registry.get_handler(tool_name)
            if handler is None:
                return format_error_response(-32602, f"Unknown tool: {tool_name}", request_id)

            result = handler(arguments)
            return format_success_response(
                {"content": [{"type": "text", "text": result}]}, request_id
            )

        except ValidationError as e:
            logger.error(f"Parameter validation error: {e}")
            return format_error_response(-32602, str(e), request_id)
        except SystemNotFoundError as e:
            logger.error(f"System not found: {e}")
            return format_error_response(-32602, str(e), request_id)
        except SystemError as e:
            logger.error(f"System execution error: {e}")
            return format_error_response(-32603, str(e), request_id)
        except ToolCallError as e:
            logger.error(f"Tool call error: {e}")
            return format_error_response(-32603, str(e), request_id)
        except Exception as e:
            logger.exception("Unexpected error in tool call")
            return format_error_response(-32603, f"Internal error: {str(e)}", request_id)
