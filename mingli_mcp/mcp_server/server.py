"""
MCP Server core implementation.

This module contains the main MingliMCPServer class that coordinates
protocol handling, tool execution, and transport management.
"""

from typing import Any, Dict, List, Optional

from mingli_mcp.config import config
from mingli_mcp.core.exceptions import (
    SystemError,
    SystemNotFoundError,
    ToolCallError,
    ValidationError,
)
from mingli_mcp.mcp_server.protocol import SUPPORTED_PROTOCOL_VERSIONS, ProtocolHandler
from mingli_mcp.mcp_server.tools import ToolRegistry
from mingli_mcp.transports import StdioTransport
from mingli_mcp.utils.formatters import format_error_response, format_success_response

logger = config.get_logger(__name__)


class MingliMCPServer:
    """命理MCP服务器"""

    def __init__(self, http_cors_origins: Optional[List[str]] = None):
        self.http_cors_origins = http_cors_origins
        self.transport = None
        self.protocol_handler = ProtocolHandler()
        self.tool_registry = ToolRegistry()
        self._initialize_transport()

    def _initialize_transport(self):
        """初始化传输层"""
        from mingli_mcp.transports import HTTP_TRANSPORT_AVAILABLE

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
            from mingli_mcp.transports import HttpTransport

            self.transport = HttpTransport(
                host=config.HTTP_HOST,
                port=config.HTTP_PORT,
                api_key=config.HTTP_API_KEY,
                enable_rate_limit=config.ENABLE_RATE_LIMIT,
                rate_limit_requests=config.RATE_LIMIT_REQUESTS,
                rate_limit_window=config.RATE_LIMIT_WINDOW,
                cors_origins=self.http_cors_origins,
                cors_allow_credentials=config.CORS_ALLOW_CREDENTIALS,
                supported_protocol_versions=SUPPORTED_PROTOCOL_VERSIONS,
            )
        else:
            raise ValueError(f"Unsupported transport type: {transport_type}")

        self.transport.set_message_handler(self.handle_request)
        logger.info(f"Initialized {transport_type} transport")

    def start(self):
        """启动MCP服务器"""
        from mingli_mcp.systems import list_systems

        logger.info(f"Starting {config.MCP_SERVER_NAME} v{config.MCP_SERVER_VERSION}")
        logger.info(f"Available systems: {', '.join(list_systems())}")
        self.transport.start()

    def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        处理MCP请求

        Args:
            request: JSON-RPC请求

        Returns:
            JSON-RPC响应；对于notification（无id的消息）返回None
        """
        method = request.get("method")
        request_id = request.get("id")
        # JSON-RPC规范：没有id成员的消息是notification，不能对其发送响应
        is_notification = "id" not in request

        try:
            # Protocol methods
            if method == "initialize":
                return self.protocol_handler.handle_initialize(request, request_id)
            elif method == "ping":
                return format_success_response({}, request_id)
            elif method == "notifications/initialized":
                logger.info("Received initialized notification")
                return None
            elif is_notification:
                # 其他notification（如notifications/cancelled）：接受但不响应
                logger.debug(f"Ignoring notification: {method}")
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
            elif method in ("resources/read", "resources/get"):
                # resources/read 是MCP标准方法名；resources/get 为历史兼容
                return self.protocol_handler.handle_resources_read(request, request_id)
            elif method == "resources/templates/list":
                return format_success_response({"resourceTemplates": []}, request_id)
            else:
                logger.warning(f"Unknown method: {method}")
                return format_error_response(-32601, f"Method not found: {method}", request_id)

        except (ValidationError, SystemNotFoundError) as e:
            logger.error(f"Request validation error for {method}: {e}")
            if is_notification:
                return None
            return format_error_response(-32602, str(e), request_id)
        except Exception as e:
            logger.exception(f"Unexpected error handling request: {method}")
            if is_notification:
                return None
            return format_error_response(-32603, f"Internal error: {str(e)}", request_id)

    def _handle_tools_call(self, request: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """处理工具调用请求"""
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
