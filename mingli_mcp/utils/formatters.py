"""
响应格式化工具
"""

from typing import Any, Dict, Optional


def format_error_response(
    error_code: int, error_message: str, request_id: Optional[Any] = None
) -> Dict[str, Any]:
    """
    格式化错误响应

    Args:
        error_code: 错误代码
        error_message: 错误消息
        request_id: 请求ID；无法确定时（如Parse error/Invalid Request）传None

    Returns:
        JSON-RPC错误响应

    Note:
        JSON-RPC 2.0规范要求响应对象必须包含id成员；
        无法从请求中确定id时必须为null，而不是省略该字段。
    """
    return {
        "jsonrpc": "2.0",
        "error": {"code": error_code, "message": error_message},
        "id": request_id,
    }


def format_success_response(result: Any, request_id: Optional[Any] = None) -> Dict[str, Any]:
    """
    格式化成功响应

    Args:
        result: 结果数据
        request_id: 请求ID

    Returns:
        JSON-RPC成功响应

    Note:
        JSON-RPC 2.0规范要求响应对象必须包含id成员（与请求id一致）。
    """
    return {"jsonrpc": "2.0", "result": result, "id": request_id}
