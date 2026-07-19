#!/usr/bin/env python3
"""
演示改进功能

展示系统缓存、性能监控等新功能的使用
"""

import sys
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mingli_mcp.systems import clear_cache, get_system, list_systems  # noqa: E402
from mingli_mcp.utils.metrics import get_metrics, record_request  # noqa: E402
from mingli_mcp.utils.rate_limiter import RateLimiter  # noqa: E402


def demo_system_cache():
    """演示系统缓存功能"""
    print("\n" + "=" * 60)
    print("演示1: 系统实例缓存")
    print("=" * 60)

    print("\n1. 首次获取系统（创建实例）:")
    start = time.time()
    system1 = get_system("ziwei")
    t1 = time.time() - start
    print(f"   系统1 ID: {id(system1)}")
    print(f"   耗时: {t1*1000:.2f}ms")

    print("\n2. 再次获取系统（使用缓存）:")
    start = time.time()
    system2 = get_system("ziwei")
    t2 = time.time() - start
    print(f"   系统2 ID: {id(system2)}")
    print(f"   耗时: {t2*1000:.2f}ms")
    print(f"   速度提升: {((t1-t2)/t1*100):.1f}%")

    print("\n3. 验证是否为同一实例:")
    print(f"   system1 is system2: {system1 is system2}")

    print("\n4. 创建独立实例（不使用缓存）:")
    start = time.time()
    system3 = get_system("ziwei", cached=False)
    t3 = time.time() - start
    print(f"   系统3 ID: {id(system3)}")
    print(f"   耗时: {t3*1000:.2f}ms")
    print(f"   system1 is system3: {system1 is system3}")

    print("\n5. 清除缓存:")
    clear_cache("ziwei")
    print("   缓存已清除")

    print("\n6. 清除后重新获取:")
    system4 = get_system("ziwei")
    print(f"   系统4 ID: {id(system4)}")
    print(f"   system1 is system4: {system1 is system4}")

    print("\n✅ 系统缓存演示完成")


def demo_rate_limiter():
    """演示限流器功能"""
    print("\n" + "=" * 60)
    print("演示2: 请求限流器")
    print("=" * 60)

    # 创建限流器：5秒内最多3个请求
    limiter = RateLimiter(max_requests=3, window_seconds=5)

    client_id = "test_client"

    print(f"\n限流配置: {limiter.max_requests}请求/{limiter.window.total_seconds()}秒")

    for i in range(5):
        allowed = limiter.is_allowed(client_id)
        remaining = limiter.get_remaining(client_id)

        print(f"\n请求 {i+1}:")
        print(f"  允许: {'✅' if allowed else '❌'}")
        print(f"  剩余: {remaining}个")

        if not allowed:
            reset_time = limiter.get_reset_time(client_id)
            print(f"  重置时间: {reset_time.strftime('%H:%M:%S')}")
            print("  提示: 请求已被限流，请稍后重试")

        time.sleep(0.5)

    print("\n等待5秒后重置...")
    time.sleep(5)

    print("\n重置后的请求:")
    allowed = limiter.is_allowed(client_id)
    remaining = limiter.get_remaining(client_id)
    print(f"  允许: {'✅' if allowed else '❌'}")
    print(f"  剩余: {remaining}个")

    print("\n限流器统计:")
    stats = limiter.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n✅ 限流器演示完成")


def demo_metrics():
    """演示性能监控功能"""
    print("\n" + "=" * 60)
    print("演示3: 性能监控")
    print("=" * 60)

    metrics = get_metrics()
    metrics.reset()  # 重置指标

    print("\n模拟一些请求...")

    # 模拟成功的请求
    for i in range(10):
        duration = 0.1 + i * 0.01  # 递增的响应时间
        system = "ziwei" if i % 2 == 0 else "bazi"
        method = "get_chart" if i % 3 == 0 else "get_fortune"
        record_request(system, method, duration, True)

    # 模拟失败的请求
    record_request("ziwei", "get_chart", 0.5, False, "ValidationError")
    record_request("bazi", "analyze_element", 0.3, False, "SystemError")

    print("\n获取统计摘要:")
    summary = metrics.get_summary()

    print("\n总体统计:")
    print(f"  运行时间: {summary['uptime_seconds']:.2f}秒")
    print(f"  总请求数: {summary['total_requests']}")
    print(f"  成功请求: {summary['successful_requests']}")
    print(f"  失败请求: {summary['failed_requests']}")
    print(f"  成功率: {summary['success_rate']:.1f}%")

    print("\n性能指标:")
    print(f"  平均响应时间: {summary['average_response_time']:.3f}秒")
    print(f"  最小响应时间: {summary['min_response_time']:.3f}秒")
    print(f"  最大响应时间: {summary['max_response_time']:.3f}秒")
    print(f"  每秒请求数: {summary['requests_per_second']:.2f}")

    print("\n系统调用:")
    for system, count in summary["system_calls"].items():
        print(f"  {system}: {count}次")

    print("\n最常调用的方法:")
    top_methods = metrics.get_top_methods(5)
    for i, (method, count) in enumerate(top_methods, 1):
        print(f"  {i}. {method}: {count}次")

    print("\n错误统计:")
    top_errors = metrics.get_top_errors(5)
    for i, (error, count) in enumerate(top_errors, 1):
        print(f"  {i}. {error}: {count}次")

    print("\n✅ 性能监控演示完成")


def demo_exception_handling():
    """演示异常处理"""
    print("\n" + "=" * 60)
    print("演示4: 异常处理")
    print("=" * 60)

    from mingli_mcp.core.exceptions import SystemNotFoundError, ValidationError

    # 1. ValidationError 示例
    print("\n1. 参数验证错误:")
    try:
        system = get_system("ziwei")
        # 故意传入错误的参数
        invalid_info = {"date": "2000-08-16", "time_index": 99, "gender": "女"}
        system.get_chart(invalid_info)
    except ValidationError as e:
        print(f"   ✅ 捕获ValidationError: {e}")

    # 2. SystemNotFoundError 示例
    print("\n2. 系统未找到错误:")
    try:
        get_system("non_existent_system")
    except SystemNotFoundError as e:
        print(f"   ✅ 捕获SystemNotFoundError: {e}")

    print("\n✅ 异常处理演示完成")


def demo_list_systems():
    """演示列出所有系统"""
    print("\n" + "=" * 60)
    print("演示5: 列出所有系统")
    print("=" * 60)

    systems = list_systems()
    print(f"\n可用的命理系统: {len(systems)}个")

    for i, system_name in enumerate(systems, 1):
        system = get_system(system_name)
        capabilities = system.get_capabilities()

        print(f"\n{i}. {system.get_system_name()} ({system_name})")
        print(f"   版本: {system.get_system_version()}")
        print("   功能:")
        for cap_name, cap_value in capabilities.items():
            status = "✅" if cap_value else "❌"
            print(f"     {status} {cap_name}")

    print("\n✅ 系统列表演示完成")


def main():
    """运行所有演示"""
    print("\n" + "🔮" * 30)
    print("命理MCP项目改进功能演示")
    print("🔮" * 30)

    demos = [
        demo_system_cache,
        demo_rate_limiter,
        demo_metrics,
        demo_exception_handling,
        demo_list_systems,
    ]

    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"\n❌ 演示失败: {e}")
            import traceback

            traceback.print_exc()

    print("\n" + "=" * 60)
    print("所有演示完成！")
    print("=" * 60)
    print("\n参考文档:")
    print("  - HIGH_PRIORITY_IMPROVEMENTS.md")
    print("  - MEDIUM_PRIORITY_IMPROVEMENTS.md")
    print("  - IMPROVEMENTS_SUMMARY.md")
    print("\n" + "🎉" * 30)


if __name__ == "__main__":
    main()
