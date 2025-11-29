#!/usr/bin/env python3
"""
性能工具测试
"""

import time

from utils.performance import PerformanceMetrics, PerformanceTimer, log_performance


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


class TestPerformanceMetrics:
    """性能指标收集器测试"""

    def test_record_single_operation(self):
        """测试记录单个操作"""
        metrics = PerformanceMetrics()
        metrics.record("op1", 0.5)

        stats = metrics.get_stats("op1")
        assert stats["count"] == 1
        assert stats["total_time"] == 0.5
        assert stats["avg_time"] == 0.5
        assert stats["min_time"] == 0.5
        assert stats["max_time"] == 0.5

    def test_record_multiple_operations(self):
        """测试记录多个操作"""
        metrics = PerformanceMetrics()
        metrics.record("op1", 0.1)
        metrics.record("op1", 0.3)
        metrics.record("op1", 0.2)

        stats = metrics.get_stats("op1")
        assert stats["count"] == 3
        assert stats["total_time"] == 0.6
        assert stats["avg_time"] == 0.2
        assert stats["min_time"] == 0.1
        assert stats["max_time"] == 0.3

    def test_multiple_operation_types(self):
        """测试多种操作类型"""
        metrics = PerformanceMetrics()
        metrics.record("op1", 0.1)
        metrics.record("op2", 0.2)
        metrics.record("op1", 0.3)

        all_stats = metrics.get_all_stats()
        assert len(all_stats) == 2

        op1_stats = metrics.get_stats("op1")
        op2_stats = metrics.get_stats("op2")

        assert op1_stats["count"] == 2
        assert op2_stats["count"] == 1

    def test_reset(self):
        """测试重置功能"""
        metrics = PerformanceMetrics()
        metrics.record("op1", 0.1)
        metrics.record("op2", 0.2)

        metrics.reset()

        all_stats = metrics.get_all_stats()
        assert len(all_stats) == 0

    def test_unknown_operation(self):
        """测试查询未知操作"""
        metrics = PerformanceMetrics()
        stats = metrics.get_stats("unknown")
        assert stats == {}
