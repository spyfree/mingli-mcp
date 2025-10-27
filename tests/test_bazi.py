#!/usr/bin/env python3
"""
八字系统测试

测试八字排盘、运势、五行分析功能
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from systems import get_system
from datetime import datetime


def test_bazi_chart():
    """测试八字排盘"""
    print("\n" + "="*60)
    print("测试八字排盘")
    print("="*60)
    
    birth_info = {
        'date': '2000-08-16',
        'time_index': 2,  # 寅时
        'gender': '女',
        'calendar': 'solar'
    }
    
    try:
        system = get_system('bazi')
        chart = system.get_chart(birth_info)
        
        print(f"\n阳历: {chart['solar_date']}")
        print(f"农历: {chart['lunar_date']}")
        print(f"性别: {chart['gender']}")
        print(f"生肖: {chart['zodiac']}")
        print(f"\n八字: {chart['eight_char']}")
        print(f"日主: {chart['day_master']}")
        
        print("\n四柱详情:")
        for pillar_name, pillar_data in chart['pillars'].items():
            print(f"  {pillar_name}柱: {pillar_data['pillar']} (干:{pillar_data['gan']} 支:{pillar_data['zhi']})")
        
        print("\n十神:")
        for pos, deity in chart['deities'].items():
            print(f"  {pos}: {deity}")
        
        print("\n五行分数:")
        for element, score in chart['wu_xing']['scores'].items():
            print(f"  {element}: {score}")
        
        print("\n✅ 排盘测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ 排盘测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bazi_fortune():
    """测试八字运势"""
    print("\n" + "="*60)
    print("测试八字运势")
    print("="*60)
    
    birth_info = {
        'date': '2000-08-16',
        'time_index': 2,
        'gender': '女',
        'calendar': 'solar'
    }
    
    try:
        system = get_system('bazi')
        fortune = system.get_fortune(birth_info, datetime.now())
        
        print(f"\n查询日期: {fortune['query_date']}")
        print(f"当前年龄: {fortune['age']}岁")
        print(f"日主: {fortune['day_master']}")
        
        print(f"\n大运:")
        print(f"  {fortune['da_yun']['description']}")
        print(f"  年龄范围: {fortune['da_yun']['age_range']}")
        
        print(f"\n流年:")
        print(f"  {fortune['liu_nian']['year']}年")
        print(f"  干支: {fortune['liu_nian']['gan_zhi']}")
        print(f"  生肖: {fortune['liu_nian']['zodiac']}")
        
        print("\n✅ 运势测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ 运势测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_element_analysis():
    """测试五行分析"""
    print("\n" + "="*60)
    print("测试五行分析")
    print("="*60)
    
    birth_info = {
        'date': '2000-08-16',
        'time_index': 2,
        'gender': '女',
        'calendar': 'solar'
    }
    
    try:
        system = get_system('bazi')
        analysis = system.analyze_element(birth_info)
        
        print(f"\n日主: {analysis['day_master']} ({analysis['day_master_element']})")
        
        print("\n五行分数:")
        for element, score in analysis['scores'].items():
            percentage = analysis['percentages'][element]
            print(f"  {element}: {score}个 ({percentage:.1f}%)")
        
        print(f"\n最旺五行: {analysis['strongest']['element']} ({analysis['strongest']['score']}个)")
        print(f"最弱五行: {analysis['weakest']['element']} ({analysis['weakest']['score']}个)")
        
        if analysis['missing']:
            print(f"缺失五行: {', '.join(analysis['missing'])}")
        else:
            print("缺失五行: 无")
        
        print(f"平衡度: {analysis['balance']}")
        
        print("\n✅ 五行分析测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ 五行分析测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_lunar_calendar():
    """测试农历输入"""
    print("\n" + "="*60)
    print("测试农历输入")
    print("="*60)
    
    birth_info = {
        'date': '2000-07-17',  # 农历
        'time_index': 2,
        'gender': '女',
        'calendar': 'lunar'
    }
    
    try:
        system = get_system('bazi')
        chart = system.get_chart(birth_info)
        
        print(f"\n农历: {chart['lunar_date']}")
        print(f"阳历: {chart['solar_date']}")
        print(f"八字: {chart['eight_char']}")
        
        print("\n✅ 农历测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ 农历测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "🔮"*20)
    print("八字系统测试")
    print("🔮"*20)
    
    tests = [
        test_bazi_chart,
        test_bazi_fortune,
        test_element_analysis,
        test_lunar_calendar,
    ]
    
    results = []
    for test_func in tests:
        results.append(test_func())
    
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n通过: {passed}/{total}")
    
    if all(results):
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n⚠️  部分测试失败")
        return 1


if __name__ == '__main__':
    exit(main())
