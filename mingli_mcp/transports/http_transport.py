"""
HTTP传输层实现

基于FastAPI实现Streamable HTTP方式的MCP服务（无状态、纯JSON响应模式）
适用于远程调用、云端部署等场景

MCP Streamable HTTP规范要点（2025-11-25）：
- 单一MCP端点（/mcp）接受POST
- 对notification/response返回202 Accepted且无body
- 必须校验Origin头，非法时返回403（防DNS rebinding）
- MCP-Protocol-Version头非法/不支持时返回400
- 不支持SSE的服务器对GET返回405（FastAPI自动处理）
"""

import logging
import secrets
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlparse

import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from starlette.concurrency import run_in_threadpool

from mingli_mcp.config import config
from mingli_mcp.utils.rate_limiter import RateLimiter

from .base_transport import BaseTransport

logger = logging.getLogger(__name__)


class HttpTransport(BaseTransport):
    """HTTP传输实现"""

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8080,
        api_key: Optional[str] = None,
        enable_rate_limit: bool = True,
        rate_limit_requests: int = 100,
        rate_limit_window: int = 60,
        cors_origins: Optional[List[str]] = None,
        cors_allow_credentials: bool = False,
        supported_protocol_versions: Optional[List[str]] = None,
    ):
        """
        初始化HTTP传输

        Args:
            host: 监听地址
            port: 监听端口
            api_key: API密钥（可选，用于认证）
            enable_rate_limit: 是否启用限流
            rate_limit_requests: 限流窗口内最大请求数
            rate_limit_window: 限流窗口大小（秒）
            cors_origins: 允许的CORS来源列表
            cors_allow_credentials: 是否允许携带凭证
            supported_protocol_versions: 支持的MCP协议版本列表（用于校验MCP-Protocol-Version头）
        """
        self.host = host
        self.port = port
        self.api_key = api_key
        self.enable_rate_limit = enable_rate_limit
        self.supported_protocol_versions = supported_protocol_versions
        self.message_handler = None  # 初始化消息处理器

        # 初始化限流器
        if self.enable_rate_limit:
            self.rate_limiter = RateLimiter(
                max_requests=rate_limit_requests, window_seconds=rate_limit_window
            )
            logger.info(
                f"Rate limiter enabled: {rate_limit_requests} requests per {rate_limit_window}s"
            )

        self.app = FastAPI(
            title="Mingli MCP Server",
            description="命理MCP服务 - HTTP API",
            version=config.MCP_SERVER_VERSION,
        )

        # CORS配置 - 从配置文件读取或使用参数
        if cors_origins is None:
            cors_origins = config.CORS_ORIGINS.split(",")

        # 过滤空字符串
        cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]

        # 如果没有配置，使用安全默认值
        if not cors_origins:
            cors_origins = ["http://localhost:3000", "http://localhost:8080"]
            logger.warning(
                "No CORS origins configured, using default: localhost only. "
                "Set CORS_ORIGINS environment variable for production."
            )

        self.cors_origins = cors_origins

        # 添加CORS支持（安全配置）
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=cors_allow_credentials or config.CORS_ALLOW_CREDENTIALS,
            allow_methods=["GET", "POST", "OPTIONS"],  # 只允许必要的方法
            allow_headers=["Content-Type", "Authorization", "MCP-Protocol-Version"],
        )

        logger.info(f"CORS enabled for origins: {cors_origins}")

        self._setup_routes()
        logger.info(f"HTTP transport initialized on {host}:{port}")

    def _get_client_id(self, request: Request) -> str:
        """获取限流用的客户端标识

        部署在Cloudflare等反向代理后面时，request.client.host是代理地址，
        优先使用CF-Connecting-IP / X-Forwarded-For还原真实客户端IP。
        """
        cf_ip = request.headers.get("CF-Connecting-IP")
        if cf_ip:
            return cf_ip
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _check_origin(self, request: Request) -> Optional[JSONResponse]:
        """校验Origin头（MCP规范要求，防DNS rebinding）

        无Origin头的请求（非浏览器客户端）直接放行；
        有Origin头但不在允许列表且与请求Host不同源时返回403。
        """
        origin = request.headers.get("Origin")
        if not origin or origin == "null":
            return None

        if "*" in self.cors_origins or origin in self.cors_origins:
            return None

        # 同源请求（Origin的host与请求Host一致）放行
        origin_host = urlparse(origin).netloc
        request_host = request.headers.get("Host", "")
        if origin_host and origin_host == request_host:
            return None

        logger.warning(f"Rejected request with invalid Origin: {origin}")
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "jsonrpc": "2.0",
                "error": {"code": -32600, "message": "Invalid Origin"},
            },
        )

    def _check_protocol_version(self, request: Request) -> Optional[JSONResponse]:
        """校验MCP-Protocol-Version头

        规范：头缺失时假定为旧版本客户端，放行；
        头存在但版本不受支持时必须返回400。
        """
        version = request.headers.get("MCP-Protocol-Version")
        if not version or not self.supported_protocol_versions:
            return None

        if version in self.supported_protocol_versions:
            return None

        logger.warning(f"Unsupported MCP-Protocol-Version: {version}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "jsonrpc": "2.0",
                "error": {
                    "code": -32600,
                    "message": f"Unsupported protocol version: {version}",
                    "data": {"supported": self.supported_protocol_versions},
                },
            },
        )

    def _check_api_key(self, request: Request, client_id: str) -> None:
        """API密钥验证（如果配置了），失败抛出401"""
        if not self.api_key:
            return
        auth_header = request.headers.get("Authorization", "")
        expected = f"Bearer {self.api_key}"
        # 使用常量时间比较防止时序攻击
        if not auth_header or not secrets.compare_digest(auth_header, expected):
            logger.warning(f"Invalid API key attempt from {client_id}")
            raise HTTPException(status_code=401, detail="Unauthorized")

    def _setup_routes(self):
        """设置路由"""

        @self.app.get("/")
        async def root():
            """根路径"""
            return {
                "name": "Mingli MCP Server",
                "version": config.MCP_SERVER_VERSION,
                "protocol": "MCP",
                "transport": "HTTP",
                "endpoints": {"mcp": "/mcp", "health": "/health", "docs": "/docs"},
            }

        @self.app.get("/health")
        async def health():
            """健康检查"""
            return {
                "status": "healthy",
                "transport": "http",
                "systems": ["ziwei", "bazi"],
                "rate_limiting": self.enable_rate_limit,
            }

        @self.app.get("/stats")
        async def stats(request: Request):
            """获取限流器统计信息（需要API key）"""
            self._check_api_key(request, self._get_client_id(request))

            if not self.enable_rate_limit:
                return {"rate_limiting": False, "message": "Rate limiting is disabled"}

            return self.rate_limiter.get_stats()

        @self.app.post("/mcp")
        async def handle_mcp(request: Request):
            """处理MCP请求（Streamable HTTP的MCP端点，纯JSON响应模式）"""
            # Origin校验（MCP规范：非法Origin必须返回403）
            origin_error = self._check_origin(request)
            if origin_error is not None:
                return origin_error

            # MCP-Protocol-Version头校验（不支持的版本必须返回400）
            version_error = self._check_protocol_version(request)
            if version_error is not None:
                return version_error

            client_id = self._get_client_id(request)

            # 限流检查
            if self.enable_rate_limit and not self.rate_limiter.is_allowed(client_id):
                reset_time = self.rate_limiter.get_reset_time(client_id)
                reset_str = reset_time.isoformat() if reset_time else "unknown"

                logger.warning(f"Rate limit exceeded for client: {client_id}")

                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Too Many Requests",
                        "message": "Rate limit exceeded. Please try again later.",
                        "reset_time": reset_str,
                    },
                    headers={
                        "X-RateLimit-Limit": str(self.rate_limiter.max_requests),
                        "X-RateLimit-Remaining": str(self.rate_limiter.get_remaining(client_id)),
                        "X-RateLimit-Reset": reset_str,
                    },
                )

            # API密钥验证（如果配置了）
            self._check_api_key(request, client_id)

            try:
                data = await request.json()
            except Exception:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "jsonrpc": "2.0",
                        "error": {"code": -32700, "message": "Parse error"},
                        "id": None,
                    },
                )

            logger.debug(
                f"Received MCP request: {data.get('method') if isinstance(data, dict) else data}"
            )

            try:
                # 调用消息处理器
                if not self.message_handler:
                    raise HTTPException(status_code=500, detail="Message handler not set")

                # 排盘计算是同步阻塞操作，放入线程池避免卡住事件循环
                response = await run_in_threadpool(self.message_handler, data)

                # notification/response消息：规范要求返回202 Accepted且无body
                if response is None:
                    return Response(status_code=status.HTTP_202_ACCEPTED)

                return JSONResponse(content=response)

            except HTTPException:
                # FastAPI 异常直接抛出
                raise
            except Exception:
                # 记录完整错误详情到日志
                logger.exception("Error handling MCP request")
                # 返回通用错误消息，不暴露内部实现细节
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "error": {"code": -32603, "message": "Internal server error"},
                        "id": data.get("id") if isinstance(data, dict) else None,
                    },
                    status_code=500,
                )

    def start(self):
        """启动HTTP服务器"""
        logger.info(f"Starting HTTP server on {self.host}:{self.port}")
        uvicorn.run(self.app, host=self.host, port=self.port, log_level="info")

    def stop(self):
        """停止HTTP服务器"""
        logger.info("HTTP server stopped")

    def send_message(self, message: Dict[str, Any]):
        """
        HTTP模式不需要主动发送消息
        响应由FastAPI自动处理
        """
        pass

    def receive_message(self) -> Optional[Dict[str, Any]]:
        """
        HTTP模式由FastAPI处理接收
        此方法不使用
        """
        pass

    def set_message_handler(self, handler: Callable[[Dict[str, Any]], Dict[str, Any]]):
        """设置消息处理器"""
        self.message_handler = handler
        logger.debug("Message handler set for HTTP transport")
