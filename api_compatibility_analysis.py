"""
API 兼容性详细分析：py-iztro vs iztro-py

测试两个库的 API 差异和兼容性问题
"""

from datetime import datetime


def test_basic_api():
    """测试基本 API"""
    print("=" * 70)
    print("API 兼容性详细分析")
    print("=" * 70)

    from py_iztro import Astro as PyIztroAstro
    from iztro_py import astro as iztro_astro

    test_data = {"date": "2000-8-16", "time_index": 2, "gender": "男"}

    print("\n1. 星盘生成 API")
    print("-" * 70)

    # py-iztro
    print("\n[py-iztro]")
    pyiztro = PyIztroAstro()
    py_astrolabe = pyiztro.by_solar(test_data["date"], test_data["time_index"], test_data["gender"])
    print(f"✓ by_solar('{test_data['date']}', {test_data['time_index']}, '{test_data['gender']}')")
    print(f"  返回类型: {type(py_astrolabe)}")

    # iztro-py
    print("\n[iztro-py]")
    iz_astrolabe = iztro_astro.by_solar(
        test_data["date"], test_data["time_index"], test_data["gender"]
    )
    print(f"✓ by_solar('{test_data['date']}', {test_data['time_index']}, '{test_data['gender']}')")
    print(f"  返回类型: {type(iz_astrolabe)}")

    print("\n2. 星盘对象属性对比")
    print("-" * 70)

    # 对比属性
    py_attrs = set(dir(py_astrolabe))
    iz_attrs = set(dir(iz_astrolabe))

    common_attrs = py_attrs & iz_attrs
    py_only = py_attrs - iz_attrs - set([a for a in py_attrs if a.startswith("_")])
    iz_only = iz_attrs - py_attrs - set([a for a in iz_attrs if a.startswith("_")])

    print(f"\n共同方法/属性 ({len(common_attrs)}):")
    common_public = [a for a in sorted(common_attrs) if not a.startswith("_")][:10]
    for attr in common_public:
        print(f"  ✓ {attr}")
    if len(common_public) > 10:
        print(f"  ... 还有 {len(common_public) - 10} 个")

    if py_only:
        print(f"\n仅 py-iztro 有 ({len(py_only)}):")
        for attr in sorted(list(py_only))[:5]:
            print(f"  • {attr}")
        if len(py_only) > 5:
            print(f"  ... 还有 {len(py_only) - 5} 个")

    if iz_only:
        print(f"\n仅 iztro-py 有 ({len(iz_only)}):")
        for attr in sorted(list(iz_only))[:5]:
            print(f"  • {attr}")
        if len(iz_only) > 5:
            print(f"  ... 还有 {len(iz_only) - 5} 个")

    print("\n3. 运势查询 API 差异 ⚠️")
    print("-" * 70)

    # py-iztro: 接受 datetime 对象
    print("\n[py-iztro] horoscope(datetime)")
    query_date_dt = datetime(2024, 1, 1)
    py_horoscope = py_astrolabe.horoscope(query_date_dt)
    print("✓ horoscope(datetime(2024, 1, 1))")
    print(f"  返回类型: {type(py_horoscope)}")

    # iztro-py: 需要字符串格式
    print("\n[iztro-py] horoscope(str, int)")
    try:
        iz_horoscope = iz_astrolabe.horoscope(query_date_dt)
        print("✓ horoscope(datetime(2024, 1, 1))")
    except AttributeError as e:
        print(f"✗ horoscope(datetime(2024, 1, 1)) - {e}")
        print("  需要使用字符串格式:")

    query_date_str = "2024-1-1"
    query_hour = 6
    iz_horoscope = iz_astrolabe.horoscope(query_date_str, query_hour)
    print(f"✓ horoscope('{query_date_str}', {query_hour})")
    print(f"  返回类型: {type(iz_horoscope)}")

    print("\n⚠️  关键差异:")
    print("  • py-iztro:  horoscope(datetime_obj)")
    print("  • iztro-py:  horoscope(date_str, hour_index)")

    print("\n4. 运势对象属性对比")
    print("-" * 70)

    # py-iztro 运势对象
    print("\n[py-iztro] 运势对象属性:")
    py_horoscope_attrs = [a for a in dir(py_horoscope) if not a.startswith("_")]
    for attr in py_horoscope_attrs[:10]:
        try:
            val = getattr(py_horoscope, attr)
            if not callable(val):
                print(f"  • {attr}: {type(val).__name__}")
        except Exception:
            pass

    # iztro-py 运势对象
    print("\n[iztro-py] 运势对象属性:")
    iz_horoscope_attrs = [a for a in dir(iz_horoscope) if not a.startswith("_")]
    for attr in iz_horoscope_attrs[:10]:
        try:
            val = getattr(iz_horoscope, attr)
            if not callable(val):
                print(f"  • {attr}: {type(val).__name__}")
        except Exception:
            pass

    print("\n5. 宫位访问 API")
    print("-" * 70)

    # py-iztro
    print("\n[py-iztro] 宫位访问:")
    try:
        if hasattr(py_astrolabe, "palace"):
            palace = py_astrolabe.palace("命宫")
            print(f"✓ palace('命宫'): {type(palace)}")
        else:
            print("✗ 不支持 palace() 方法")
            print("  需要通过其他方式访问宫位")
    except Exception as e:
        print(f"✗ palace('命宫') 失败: {e}")

    # iztro-py
    print("\n[iztro-py] 宫位访问:")
    try:
        palace = iz_astrolabe.palace("命宫")
        print(f"✓ palace('命宫'): {type(palace)}")

        # 测试宫位方法
        if hasattr(palace, "name"):
            print(f"  宫位名称: {palace.name}")
        if hasattr(palace, "stars"):
            print(f"  星曜数量: {len(palace.stars) if palace.stars else 0}")
    except Exception as e:
        print(f"✗ palace('命宫') 失败: {e}")

    print("\n6. 星曜访问 API")
    print("-" * 70)

    # iztro-py
    print("\n[iztro-py] 星曜访问:")
    try:
        star = iz_astrolabe.star("紫微")
        print(f"✓ star('紫微'): {type(star)}")

        if hasattr(star, "name"):
            print(f"  星曜名称: {star.name}")
        if hasattr(star, "brightness"):
            print(f"  亮度: {star.brightness}")
    except Exception as e:
        print(f"✗ star('紫微') 失败: {e}")

    print("\n7. 返回数据结构对比")
    print("-" * 70)

    # py-iztro 数据结构
    print("\n[py-iztro] 数据结构:")
    print(f"  星盘类型: {type(py_astrolabe).__name__}")
    if hasattr(py_astrolabe, "palaces"):
        print(f"  palaces 类型: {type(py_astrolabe.palaces).__name__}")
    if hasattr(py_astrolabe, "stars"):
        print(f"  stars 类型: {type(py_astrolabe.stars).__name__}")

    # iztro-py 数据结构
    print("\n[iztro-py] 数据结构:")
    print(f"  星盘类型: {type(iz_astrolabe).__name__}")
    if hasattr(iz_astrolabe, "palaces"):
        print(f"  palaces 类型: {type(iz_astrolabe.palaces).__name__}")
    if hasattr(iz_astrolabe, "stars"):
        print(f"  stars 类型: {type(iz_astrolabe.stars).__name__}")


def test_lunar_api():
    """测试农历 API"""
    print("\n8. 农历日期支持")
    print("-" * 70)

    from py_iztro import Astro as PyIztroAstro
    from iztro_py import astro as iztro_astro

    test_data = {
        "date": "2000-06-15",  # 农历
        "time_index": 2,
        "gender": "男",
        "is_leap_month": False,
    }

    # py-iztro
    print("\n[py-iztro] by_lunar:")
    try:
        pyiztro = PyIztroAstro()
        _py_astrolabe = pyiztro.by_lunar(  # noqa: F841
            test_data["date"],
            test_data["time_index"],
            test_data["gender"],
            test_data["is_leap_month"],
        )
        print(
            f"✓ by_lunar('{test_data['date']}', {test_data['time_index']}, "
            f"'{test_data['gender']}', {test_data['is_leap_month']})"
        )
    except Exception as e:
        print(f"✗ by_lunar 失败: {e}")

    # iztro-py
    print("\n[iztro-py] by_lunar:")
    try:
        _iz_astrolabe = iztro_astro.by_lunar(  # noqa: F841
            test_data["date"],
            test_data["time_index"],
            test_data["gender"],
            test_data["is_leap_month"],
        )
        print(
            f"✓ by_lunar('{test_data['date']}', {test_data['time_index']}, "
            f"'{test_data['gender']}', {test_data['is_leap_month']})"
        )
    except Exception as e:
        print(f"✗ by_lunar 失败: {e}")


def main():
    """运行所有测试"""
    print("\n" + "📋" * 35)
    print("py-iztro vs iztro-py API 兼容性详细分析")
    print("📋" * 35 + "\n")

    test_basic_api()
    test_lunar_api()

    print("\n" + "=" * 70)
    print("总结")
    print("=" * 70)
    print(
        """
主要差异:

1. ✓ 基本API兼容: by_solar(), by_lunar() 参数一致

2. ⚠️  运势查询差异:
   - py-iztro:  horoscope(datetime_object)
   - iztro-py:  horoscope(date_string, hour_index)

3. ✓ iztro-py 提供更丰富的方法:
   - palace(): 直接访问宫位
   - star(): 直接访问星曜
   - 链式调用支持

4. 📊 数据结构可能不同:
   - 需要测试数据序列化兼容性
   - 建议使用 formatter 层统一输出格式

迁移建议:
- 需要修改 horoscope() 调用方式
- 可利用 iztro-py 的增强 API 简化代码
- 测试所有数据访问路径
    """
    )


if __name__ == "__main__":
    main()
