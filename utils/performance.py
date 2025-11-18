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
            logger.log(
                self.log_level, f"{self.operation_name} 完成，耗时: {self.elapsed:.3f}s"
            )
        else:
            logger.error(
                f"{self.operation_name} 失败，耗时: {self.elapsed:.3f}s，错误: {exc_val}"
            )
        return False


class PerformanceMetrics:
    """
    性能指标收集器

    收集并统计函数调用次数和平均执行时间
    """

    def __init__(self):
        self.metrics = {}

    def record(self, operation: str, elapsed: float):
        """
        记录一次操作

        Args:
            operation: 操作名称
            elapsed: 耗时（秒）
        """
        if operation not in self.metrics:
            self.metrics[operation] = {"count": 0, "total_time": 0.0, "min": float("inf"), "max": 0.0}

        self.metrics[operation]["count"] += 1
        self.metrics[operation]["total_time"] += elapsed
        self.metrics[operation]["min"] = min(self.metrics[operation]["min"], elapsed)
        self.metrics[operation]["max"] = max(self.metrics[operation]["max"], elapsed)

    def get_stats(self, operation: str) -> dict:
        """
        获取操作统计信息

        Args:
            operation: 操作名称

        Returns:
            统计信息字典
        """
        if operation not in self.metrics:
            return {}

        data = self.metrics[operation]
        avg_time = data["total_time"] / data["count"] if data["count"] > 0 else 0

        return {
            "operation": operation,
            "count": data["count"],
            "total_time": round(data["total_time"], 3),
            "avg_time": round(avg_time, 3),
            "min_time": round(data["min"], 3),
            "max_time": round(data["max"], 3),
        }

    def get_all_stats(self) -> list:
        """
        获取所有操作的统计信息

        Returns:
            统计信息列表
        """
        return [self.get_stats(op) for op in self.metrics.keys()]

    def reset(self):
        """重置所有统计信息"""
        self.metrics = {}


# 全局性能指标收集器
global_metrics = PerformanceMetrics()
