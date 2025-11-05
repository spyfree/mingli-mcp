#!/usr/bin/env python3
"""
测试安全修复的独立验证脚本
不依赖外部库，直接验证代码修复
"""

import re
import sys
from pathlib import Path


def test_path_traversal_fix():
    """测试路径遍历漏洞修复"""
    print("🔍 测试路径遍历漏洞修复...")

    with open("mingli_mcp.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 检查是否添加了路径验证
    checks = [
        (r'if "/" in name or "\\\\" in name', "检查斜杠"),
        (r'from pathlib import Path', "使用 pathlib"),
        (r'\.resolve\(\)\.relative_to\(', "路径安全验证"),
        (r'logger\.warning.*path traversal', "记录攻击尝试"),
    ]

    passed = 0
    for pattern, desc in checks:
        if re.search(pattern, content):
            print(f"  ✅ {desc}")
            passed += 1
        else:
            print(f"  ❌ {desc} - 未找到")

    return passed == len(checks)


def test_timing_attack_fix():
    """测试时序攻击漏洞修复"""
    print("\n🔍 测试时序攻击漏洞修复...")

    with open("transports/http_transport.py", "r", encoding="utf-8") as f:
        content = f.read()

    checks = [
        (r'import secrets', "导入 secrets 模块"),
        (r'secrets\.compare_digest', "使用常量时间比较"),
        (r'logger\.warning.*Invalid API key', "记录无效密钥尝试"),
    ]

    passed = 0
    for pattern, desc in checks:
        if re.search(pattern, content):
            print(f"  ✅ {desc}")
            passed += 1
        else:
            print(f"  ❌ {desc} - 未找到")

    # 检查是否移除了直接字符串比较
    if re.search(r'auth_header\s*!=\s*f"Bearer', content):
        print(f"  ❌ 仍在使用不安全的字符串比较")
        return False

    print(f"  ✅ 已移除不安全的字符串比较")
    passed += 1

    return passed == len(checks) + 1


def test_info_disclosure_fix():
    """测试信息泄露漏洞修复"""
    print("\n🔍 测试信息泄露漏洞修复...")

    with open("transports/http_transport.py", "r", encoding="utf-8") as f:
        content = f.read()

    checks = [
        (r'data\s*=\s*None', "初始化 data 变量"),
        (r'"message":\s*"Internal server error"', "使用通用错误消息"),
        (r'logger\.exception.*Error handling', "记录完整错误到日志"),
        (r'except HTTPException:', "正确处理 HTTPException"),
    ]

    passed = 0
    for pattern, desc in checks:
        if re.search(pattern, content):
            print(f"  ✅ {desc}")
            passed += 1
        else:
            print(f"  ❌ {desc} - 未找到")

    # 检查是否移除了详细错误暴露
    if re.search(r'"message":\s*f"Internal error:\s*\{str\(e\)\}"', content):
        print(f"  ❌ 仍在暴露详细错误信息")
        return False

    return passed == len(checks)


def test_cors_hardening():
    """测试 CORS 配置加固"""
    print("\n🔍 测试 CORS 配置加固...")

    # 检查配置文件
    with open("config.py", "r", encoding="utf-8") as f:
        config_content = f.read()

    config_checks = [
        (r'CORS_ORIGINS:', "添加 CORS_ORIGINS 配置"),
        (r'CORS_ALLOW_CREDENTIALS:', "添加 CORS_ALLOW_CREDENTIALS 配置"),
        (r'localhost', "默认只允许本地访问"),
    ]

    # 检查 HTTP transport
    with open("transports/http_transport.py", "r", encoding="utf-8") as f:
        transport_content = f.read()

    transport_checks = [
        (r'from config import config', "导入配置"),
        (r'allow_origins=cors_origins', "使用配置的 origins"),
        (r'allow_methods=\["GET", "POST", "OPTIONS"\]', "限制 HTTP 方法"),
        (r'allow_headers=\["Content-Type", "Authorization"\]', "限制 HTTP 头"),
        (r'No CORS origins configured', "警告未配置 CORS"),
    ]

    passed = 0
    total = len(config_checks) + len(transport_checks)

    for pattern, desc in config_checks:
        if re.search(pattern, config_content):
            print(f"  ✅ {desc}")
            passed += 1
        else:
            print(f"  ❌ {desc} - 未找到")

    for pattern, desc in transport_checks:
        if re.search(pattern, transport_content):
            print(f"  ✅ {desc}")
            passed += 1
        else:
            print(f"  ❌ {desc} - 未找到")

    # 检查是否移除了 allow_origins=["*"]
    if re.search(r'allow_origins=\["\*"\]', transport_content):
        print(f"  ❌ 仍在使用不安全的 CORS 配置 (allow all)")
        return False

    print(f"  ✅ 已移除不安全的通配符配置")
    passed += 1

    return passed == total + 1


def main():
    """运行所有安全测试"""
    print("=" * 60)
    print("安全修复验证测试")
    print("=" * 60)

    tests = [
        ("路径遍历漏洞修复", test_path_traversal_fix),
        ("时序攻击漏洞修复", test_timing_attack_fix),
        ("信息泄露漏洞修复", test_info_disclosure_fix),
        ("CORS 配置加固", test_cors_hardening),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ 测试 '{name}' 失败: {e}")
            results.append((name, False))

    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")

    print("\n" + "=" * 60)
    if passed == total:
        print(f"🎉 所有测试通过！({passed}/{total})")
        print("=" * 60)
        return 0
    else:
        print(f"⚠️  部分测试失败: {passed}/{total} 通过")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
