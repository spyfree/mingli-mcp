#!/usr/bin/env python3
"""
性能工具测试
"""

import time

from mingli_mcp.utils.performance import PerformanceTimer, log_performance


class TestPerformanceTimer:
    """性能计时器测试"""

    def test_timer_basic(self):
        """测试基本计时功能"""
        with PerformanceTimer("test_operation") as timer:
            time.sleep(0.01)  # 睡眠10ms

        assert timer.elapsed is not None
        assert timer.elapsed >= 0.01
        assert timer.elapsed < 0.15  # 允许更多误差，适应CI/CD环境

    def test_timer_with_exception(self):
        """测试异常时的计时"""
        try:
            with PerformanceTimer("test_error") as timer:
                time.sleep(0.01)
                raise ValueError("Test error")
        except ValueError:
            pass

        assert timer.elapsed is not None
        assert timer.elapsed >= 0.01


class TestLogPerformance:
    """性能日志装饰器测试"""

    def test_decorator_success(self):
        """测试装饰器成功情况"""

        @log_performance
        def test_func():
            time.sleep(0.01)
            return "success"

        result = test_func()
        assert result == "success"

    def test_decorator_with_exception(self):
        """测试装饰器异常情况"""

        @log_performance
        def test_func_error():
            time.sleep(0.01)
            raise ValueError("Test error")

        try:
            test_func_error()
        except ValueError as e:
            assert str(e) == "Test error"
