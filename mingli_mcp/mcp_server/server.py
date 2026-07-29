"""
MCP Server core implementation.

This module contains the main MingliMCPServer class that coordinates
protocol handling, tool execution, and transport management.
"""

import time
from typing import Any, Dict, List, Optional

from mingli_mcp.config import config
from mingli_mcp.core.exceptions import (
    SystemError,
    SystemNotFoundError,
    ToolCallError,
    ValidationError,
)
from mingli_mcp.mcp_server.protocol import (
    MODERN_PROTOCOL_VERSIONS,
    SUPPORTED_PROTOCOL_VERSIONS,
    UNSUPPORTED_PROTOCOL_VERSION_ERROR,
    ProtocolHandler,
    get_request_protocol_version,
)
from mingli_mcp.mcp_server.tools import ToolRegistry
from mingli_mcp.transports import BaseTransport, StdioTransport
from mingli_mcp.utils.formatters import format_error_response, format_success_response
from mingli_mcp.utils.metrics import record_request

logger = config.get_logger(__name__)


class MingliMCPServer:
    """命理MCP服务器"""

    def __init__(self, http_cors_origins: Optional[List[str]] = None):
        self.http_cors_origins = http_cors_origins
        # _initialize_transport 要么赋值，要么抛异常，因此这里不需要None初始值
        self.transport: BaseTransport
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
                trust_proxy_headers=config.TRUST_PROXY_HEADERS,
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
        # JSON-RPC规范：请求必须是对象。数组（批处理）和标量都是Invalid Request。
        # 这里必须先挡住，否则下面的 request.get 会抛 AttributeError，
        # 在stdio模式下会直接终结消息循环（整个会话挂死）。
        if not isinstance(request, dict):
            logger.warning(f"Received non-object JSON-RPC message: {type(request).__name__}")
            return format_error_response(
                -32600,
                "Invalid Request: JSON-RPC message must be an object",
                None,
            )

        method = request.get("method")
        request_id = request.get("id")
        # JSON-RPC规范：没有id成员的消息是notification，不能对其发送响应
        is_notification = "id" not in request

        # method必须是字符串，否则无法路由
        if not isinstance(method, str):
            logger.warning(f"Received JSON-RPC message with invalid method: {method!r}")
            if is_notification:
                return None
            return format_error_response(
                -32600, "Invalid Request: 'method' must be a string", request_id
            )

        # 2026-07-28 无状态协议：请求可在 params._meta 中声明协议版本；
        # 声明了不支持的版本时必须返回 UnsupportedProtocolVersionError
        meta_version = get_request_protocol_version(request)
        if meta_version is not None and meta_version not in SUPPORTED_PROTOCOL_VERSIONS:
            logger.warning(f"Unsupported protocol version in request _meta: {meta_version}")
            if is_notification:
                return None
            return format_error_response(
                UNSUPPORTED_PROTOCOL_VERSION_ERROR,
                f"Unsupported protocol version: {meta_version}",
                request_id,
                data={
                    "supported": SUPPORTED_PROTOCOL_VERSIONS,
                    "requested": meta_version,
                },
            )

        try:
            response = self._route_request(request, method, request_id, is_notification)
        except (ValidationError, SystemNotFoundError) as e:
            logger.error(f"Request validation error for {method}: {e}")
            if is_notification:
                return None
            response = format_error_response(-32602, str(e), request_id)
        except Exception as e:
            logger.exception(f"Unexpected error handling request: {method}")
            if is_notification:
                return None
            response = format_error_response(-32603, f"Internal error: {str(e)}", request_id)

        # 现代请求的成功结果补齐 resultType / serverInfo / 缓存提示；
        # 旧时代请求的响应保持原样
        if response is not None and meta_version in MODERN_PROTOCOL_VERSIONS:
            self.protocol_handler.decorate_modern_result(response, method)
        return response

    def _route_request(
        self, request: Dict[str, Any], method: str, request_id: Any, is_notification: bool
    ) -> Optional[Dict[str, Any]]:
        """按method路由到对应的处理器"""
        # Protocol methods
        if method == "initialize":
            return self.protocol_handler.handle_initialize(request, request_id)
        elif method == "ping":
            return format_success_response({}, request_id)
        elif method == "server/discover":
            # 2026-07-28 无状态发现（双时代客户端也用作stdio时代探测）
            return self.protocol_handler.handle_server_discover(request, request_id)
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

    @staticmethod
    def _split_tool_name(tool_name: Any) -> tuple:
        """把工具名拆成 (系统, 方法) 供指标分组用

        get_ziwei_chart -> (ziwei, get_chart)；无法识别归到 (server, <原名>)。
        """
        if not isinstance(tool_name, str):
            return "server", "unknown"

        for system in ("ziwei", "bazi"):
            marker = f"_{system}_"
            if marker in tool_name:
                verb, _, subject = tool_name.partition(marker)
                return system, f"{verb}_{subject}"
        return "server", tool_name

    def _handle_tools_call(self, request: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """处理工具调用请求"""
        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        logger.info(f"Tool call: {tool_name}")
        logger.debug(f"Arguments: {arguments}")

        system, method = self._split_tool_name(tool_name)
        started = time.monotonic()

        def record(success: bool, error_type: Optional[str] = None) -> None:
            record_request(system, method, time.monotonic() - started, success, error_type)

        try:
            handler = self.tool_registry.get_handler(tool_name)
            if handler is None:
                record(False, "UnknownTool")
                return format_error_response(-32602, f"Unknown tool: {tool_name}", request_id)

            result = handler(arguments)
            record(True)
            return format_success_response(
                {"content": [{"type": "text", "text": result}]}, request_id
            )

        except ValidationError as e:
            logger.error(f"Parameter validation error: {e}")
            record(False, type(e).__name__)
            return format_error_response(-32602, str(e), request_id)
        except SystemNotFoundError as e:
            logger.error(f"System not found: {e}")
            record(False, type(e).__name__)
            return format_error_response(-32602, str(e), request_id)
        except SystemError as e:
            logger.error(f"System execution error: {e}")
            record(False, type(e).__name__)
            return format_error_response(-32603, str(e), request_id)
        except ToolCallError as e:
            logger.error(f"Tool call error: {e}")
            record(False, type(e).__name__)
            return format_error_response(-32603, str(e), request_id)
        except Exception as e:
            logger.exception("Unexpected error in tool call")
            record(False, type(e).__name__)
            return format_error_response(-32603, f"Internal error: {str(e)}", request_id)
