"""
性能监控工具
"""

import functools
import logging
import time
from typing import Any, Callable

logger = logging.getLogger(__name__)


def log_performance(func: Callable) -> Callable:
    """
    装饰器：记录函数执行时间

    Args:
        func: 被装饰的函数

    Returns:
        装饰后的函数
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.debug(f"{func.__name__} 执行时间: {elapsed:.3f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"{func.__name__} 执行失败 (耗时: {elapsed:.3f}s): {e}")
            raise

    return wrapper


class PerformanceTimer:
    """
    性能计时器上下文管理器

    用法:
        with PerformanceTimer("排盘计算"):
            # 执行耗时操作
            pass
    """

    def __init__(self, operation_name: str, log_level: int = logging.DEBUG):
        """
        初始化计时器

        Args:
            operation_name: 操作名称
            log_level: 日志级别
        """
        self.operation_name = operation_name
        self.log_level = log_level
        self.start_time = None
        self.elapsed = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.time() - self.start_time
        if exc_type is None:
            logger.log(self.log_level, f"{self.operation_name} 完成，耗时: {self.elapsed:.3f}s")
        else:
            logger.error(f"{self.operation_name} 失败，耗时: {self.elapsed:.3f}s，错误: {exc_val}")
        return False
