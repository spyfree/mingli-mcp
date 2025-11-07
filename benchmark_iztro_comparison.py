"""
性能对比测试：py-iztro vs iztro-py

测试两个库的性能差异，包括：
1. 导入时间
2. 星盘生成时间
3. 运势计算时间
4. 内存使用
"""

import time
import tracemalloc
from datetime import datetime


def benchmark_import():
    """对比导入时间"""
    print("=" * 60)
    print("测试 1: 导入时间对比")
    print("=" * 60)

    # 测试 py-iztro
    print("\n1.1 测试 py-iztro 导入...")
    start = time.perf_counter()
    try:
        from py_iztro import Astro as PyIztroAstro  # noqa: F401

        end = time.perf_counter()
        pyiztro_time = end - start
        print(f"   ✓ py-iztro 导入成功: {pyiztro_time:.4f} 秒")
        pyiztro_available = True
    except ImportError as e:
        print(f"   ✗ py-iztro 导入失败: {e}")
        pyiztro_available = False
        pyiztro_time = None

    # 测试 iztro-py
    print("\n1.2 测试 iztro-py 导入...")
    start = time.perf_counter()
    try:
        from iztro_py import astro as iztro_astro  # noqa: F401

        end = time.perf_counter()
        iztropy_time = end - start
        print(f"   ✓ iztro-py 导入成功: {iztropy_time:.4f} 秒")
        iztropy_available = True
    except ImportError as e:
        print(f"   ✗ iztro-py 导入失败: {e}")
        iztropy_available = False
        iztropy_time = None

    # 对比结果
    if pyiztro_time and iztropy_time:
        speedup = pyiztro_time / iztropy_time
        print("\n📊 导入时间对比:")
        print(f"   py-iztro:  {pyiztro_time:.4f} 秒")
        print(f"   iztro-py:  {iztropy_time:.4f} 秒")
        print(f"   性能提升:  {speedup:.2f}x" if speedup > 1 else f"   性能降低:  {1/speedup:.2f}x")

    return pyiztro_available, iztropy_available


def benchmark_chart_generation(iterations=100):
    """对比星盘生成性能"""
    print("\n" + "=" * 60)
    print(f"测试 2: 星盘生成性能 (运行 {iterations} 次)")
    print("=" * 60)

    test_data = {"date": "2000-8-16", "time_index": 2, "gender": "男"}

    # 测试 py-iztro
    try:
        from py_iztro import Astro as PyIztroAstro

        pyiztro = PyIztroAstro()

        print(f"\n2.1 测试 py-iztro 星盘生成 ({iterations} 次)...")
        tracemalloc.start()
        start = time.perf_counter()

        for _ in range(iterations):
            astrolabe = pyiztro.by_solar(  # noqa: F841
                test_data["date"], test_data["time_index"], test_data["gender"]
            )

        end = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        pyiztro_time = end - start
        pyiztro_avg = pyiztro_time / iterations
        pyiztro_mem = peak / 1024 / 1024  # MB

        print(f"   ✓ 总时间: {pyiztro_time:.4f} 秒")
        print(f"   ✓ 平均时间: {pyiztro_avg:.6f} 秒/次")
        print(f"   ✓ 峰值内存: {pyiztro_mem:.2f} MB")

    except Exception as e:
        print(f"   ✗ py-iztro 测试失败: {e}")
        pyiztro_time = None
        pyiztro_avg = None
        pyiztro_mem = None

    # 测试 iztro-py
    try:
        from iztro_py import astro

        print(f"\n2.2 测试 iztro-py 星盘生成 ({iterations} 次)...")
        tracemalloc.start()
        start = time.perf_counter()

        for _ in range(iterations):
            _astrolabe = astro.by_solar(  # noqa: F841
                test_data["date"], test_data["time_index"], test_data["gender"]
            )

        end = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        iztropy_time = end - start
        iztropy_avg = iztropy_time / iterations
        iztropy_mem = peak / 1024 / 1024  # MB

        print(f"   ✓ 总时间: {iztropy_time:.4f} 秒")
        print(f"   ✓ 平均时间: {iztropy_avg:.6f} 秒/次")
        print(f"   ✓ 峰值内存: {iztropy_mem:.2f} MB")

    except Exception as e:
        print(f"   ✗ iztro-py 测试失败: {e}")
        iztropy_time = None
        iztropy_avg = None
        iztropy_mem = None

    # 对比结果
    if pyiztro_time and iztropy_time:
        speedup = pyiztro_time / iztropy_time
        mem_ratio = pyiztro_mem / iztropy_mem if iztropy_mem > 0 else 0

        print("\n📊 星盘生成性能对比:")
        print(f"   py-iztro:  {pyiztro_avg:.6f} 秒/次, {pyiztro_mem:.2f} MB")
        print(f"   iztro-py:  {iztropy_avg:.6f} 秒/次, {iztropy_mem:.2f} MB")
        if speedup > 1:
            print(f"   ⚡ iztro-py 快 {speedup:.2f}x")
        else:
            print(f"   ⚠️  iztro-py 慢 {1/speedup:.2f}x")

        if mem_ratio > 1:
            print(f"   💾 iztro-py 内存少 {mem_ratio:.2f}x")
        else:
            print(f"   💾 iztro-py 内存多 {1/mem_ratio:.2f}x")


def benchmark_horoscope(iterations=50):
    """对比运势计算性能"""
    print("\n" + "=" * 60)
    print(f"测试 3: 运势计算性能 (运行 {iterations} 次)")
    print("=" * 60)

    test_data = {"date": "2000-8-16", "time_index": 2, "gender": "男"}
    query_date = datetime(2024, 1, 1)

    # 测试 py-iztro
    try:
        from py_iztro import Astro as PyIztroAstro

        pyiztro = PyIztroAstro()

        print(f"\n3.1 测试 py-iztro 运势计算 ({iterations} 次)...")
        astrolabe = pyiztro.by_solar(
            test_data["date"], test_data["time_index"], test_data["gender"]
        )

        tracemalloc.start()
        start = time.perf_counter()

        for _ in range(iterations):
            _horoscope = astrolabe.horoscope(query_date)  # noqa: F841

        end = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        pyiztro_time = end - start
        pyiztro_avg = pyiztro_time / iterations
        pyiztro_mem = peak / 1024 / 1024

        print(f"   ✓ 总时间: {pyiztro_time:.4f} 秒")
        print(f"   ✓ 平均时间: {pyiztro_avg:.6f} 秒/次")
        print(f"   ✓ 峰值内存: {pyiztro_mem:.2f} MB")

    except Exception as e:
        print(f"   ✗ py-iztro 测试失败: {e}")
        pyiztro_time = None
        pyiztro_avg = None
        pyiztro_mem = None

    # 测试 iztro-py
    try:
        from iztro_py import astro

        print(f"\n3.2 测试 iztro-py 运势计算 ({iterations} 次)...")
        astrolabe = astro.by_solar(test_data["date"], test_data["time_index"], test_data["gender"])

        tracemalloc.start()
        start = time.perf_counter()

        for _ in range(iterations):
            _horoscope = astrolabe.horoscope(query_date)  # noqa: F841

        end = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        iztropy_time = end - start
        iztropy_avg = iztropy_time / iterations
        iztropy_mem = peak / 1024 / 1024

        print(f"   ✓ 总时间: {iztropy_time:.4f} 秒")
        print(f"   ✓ 平均时间: {iztropy_avg:.6f} 秒/次")
        print(f"   ✓ 峰值内存: {iztropy_mem:.2f} MB")

    except Exception as e:
        print(f"   ✗ iztro-py 测试失败: {e}")
        iztropy_time = None
        iztropy_avg = None
        iztropy_mem = None

    # 对比结果
    if pyiztro_time and iztropy_time:
        speedup = pyiztro_time / iztropy_time
        mem_ratio = pyiztro_mem / iztropy_mem if iztropy_mem > 0 else 0

        print("\n📊 运势计算性能对比:")
        print(f"   py-iztro:  {pyiztro_avg:.6f} 秒/次, {pyiztro_mem:.2f} MB")
        print(f"   iztro-py:  {iztropy_avg:.6f} 秒/次, {iztropy_mem:.2f} MB")
        if speedup > 1:
            print(f"   ⚡ iztro-py 快 {speedup:.2f}x")
        else:
            print(f"   ⚠️  iztro-py 慢 {1/speedup:.2f}x")

        if mem_ratio > 1:
            print(f"   💾 iztro-py 内存少 {mem_ratio:.2f}x")
        else:
            print(f"   💾 iztro-py 内存多 {1/mem_ratio:.2f}x")


def test_api_compatibility():
    """测试 API 兼容性"""
    print("\n" + "=" * 60)
    print("测试 4: API 兼容性检查")
    print("=" * 60)

    test_data = {"date": "2000-8-16", "time_index": 2, "gender": "男"}

    compatible = True
    issues = []

    try:
        from py_iztro import Astro as PyIztroAstro
        from iztro_py import astro as iztro_astro

        # 测试 by_solar
        print("\n4.1 测试 by_solar() 方法...")
        py_astrolabe = PyIztroAstro().by_solar(
            test_data["date"], test_data["time_index"], test_data["gender"]
        )
        iz_astrolabe = iztro_astro.by_solar(
            test_data["date"], test_data["time_index"], test_data["gender"]
        )
        print("   ✓ 两个库都支持 by_solar()")

        # 测试 horoscope
        print("\n4.2 测试 horoscope() 方法...")
        query_date = datetime(2024, 1, 1)
        _py_horoscope = py_astrolabe.horoscope(query_date)  # noqa: F841
        _iz_horoscope = iz_astrolabe.horoscope(query_date)  # noqa: F841
        print("   ✓ 两个库都支持 horoscope()")

        # 检查关键属性
        print("\n4.3 检查星盘对象属性...")
        py_attrs = dir(py_astrolabe)
        iz_attrs = dir(iz_astrolabe)

        key_methods = ["palace", "star", "horoscope"]
        for method in key_methods:
            if method in py_attrs and method in iz_attrs:
                print(f"   ✓ 方法 {method}() 都支持")
            elif method in iz_attrs:
                print(f"   ✓ 方法 {method}() 仅 iztro-py 支持")
            else:
                print(f"   ⚠️  方法 {method}() 缺失")
                compatible = False
                issues.append(f"缺失方法: {method}")

        print(f"\n📊 API 兼容性: {'✓ 兼容' if compatible else '⚠️ 存在差异'}")
        if issues:
            print("   问题列表:")
            for issue in issues:
                print(f"   - {issue}")

    except Exception as e:
        print(f"\n✗ API 兼容性测试失败: {e}")
        import traceback

        traceback.print_exc()


def main():
    """运行所有测试"""
    print("\n" + "🔬" * 30)
    print("py-iztro vs iztro-py 性能对比测试")
    print("🔬" * 30 + "\n")

    # 1. 导入时间
    pyiztro_available, iztropy_available = benchmark_import()

    if not iztropy_available:
        print("\n⚠️  iztro-py 未安装，请先安装: pip install iztro-py")
        return

    if not pyiztro_available:
        print("\n⚠️  py-iztro 未安装，无法对比")
        return

    # 2. 星盘生成性能
    benchmark_chart_generation(iterations=100)

    # 3. 运势计算性能
    benchmark_horoscope(iterations=50)

    # 4. API 兼容性
    test_api_compatibility()

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
