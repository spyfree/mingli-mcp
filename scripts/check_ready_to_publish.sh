#!/bin/bash
# PyPI发布前检查脚本

echo "🔍 检查PyPI发布准备情况..."
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# 检查函数
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} $2 存在"
        return 0
    else
        echo -e "${RED}❌${NC} $2 缺失"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

check_content() {
    if grep -q "$2" "$1"; then
        echo -e "${GREEN}✅${NC} $3"
        return 0
    else
        echo -e "${YELLOW}⚠️${NC} $3"
        WARNINGS=$((WARNINGS + 1))
        return 1
    fi
}

echo "📋 必需文件检查"
echo "─────────────────────────────────────"
check_file "LICENSE" "LICENSE文件"
check_file "README.md" "README文件"
check_file "pyproject.toml" "pyproject.toml文件"
check_file "MANIFEST.in" "MANIFEST.in文件"
check_file "mingli_mcp.py" "主入口文件"
check_file "requirements.txt" "依赖文件"
echo ""

echo "📝 配置检查"
echo "─────────────────────────────────────"
if [ -f "pyproject.toml" ]; then
    check_content "pyproject.toml" "version" "版本号已设置"
    check_content "pyproject.toml" "name.*=" "包名已设置"
    check_content "pyproject.toml" "authors" "作者信息已设置"
    
    if grep -q "Your Name" "pyproject.toml"; then
        echo -e "${YELLOW}⚠️${NC} 作者信息需要更新（当前为默认值）"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    if grep -q "yourusername" "pyproject.toml"; then
        echo -e "${YELLOW}⚠️${NC} GitHub链接需要更新"
        WARNINGS=$((WARNINGS + 1))
    fi
fi
echo ""

echo "🗂️  目录结构检查"
echo "─────────────────────────────────────"
check_file "core/__init__.py" "core模块"
check_file "systems/__init__.py" "systems模块"
check_file "transports/__init__.py" "transports模块"
check_file "utils/__init__.py" "utils模块"
echo ""

echo "🧪 构建工具检查"
echo "─────────────────────────────────────"
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✅${NC} Python3 已安装"
    python3 --version
else
    echo -e "${RED}❌${NC} Python3 未安装"
    ERRORS=$((ERRORS + 1))
fi

# 使用当前Python环境
PYTHON_CMD="python3"
if [ -n "$VIRTUAL_ENV" ]; then
    PYTHON_CMD="python"
fi

if $PYTHON_CMD -c "import build" 2>/dev/null; then
    echo -e "${GREEN}✅${NC} build 已安装"
else
    echo -e "${YELLOW}⚠️${NC} build 未安装（运行: pip install build）"
    WARNINGS=$((WARNINGS + 1))
fi

if $PYTHON_CMD -c "import twine" 2>/dev/null; then
    echo -e "${GREEN}✅${NC} twine 已安装"
else
    echo -e "${YELLOW}⚠️${NC} twine 未安装（运行: pip install twine）"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

echo "🧹 清理检查"
echo "─────────────────────────────────────"
if [ -d "dist" ] || [ -d "build" ] || [ -d "*.egg-info" ]; then
    echo -e "${YELLOW}⚠️${NC} 存在旧的构建文件，建议清理"
    echo "   运行: rm -rf dist/ build/ *.egg-info"
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}✅${NC} 无旧构建文件"
fi

if [ -f ".env" ]; then
    if grep -q ".env" ".gitignore"; then
        echo -e "${GREEN}✅${NC} .env 已添加到 .gitignore"
    else
        echo -e "${RED}❌${NC} .env 未添加到 .gitignore（可能泄露密钥）"
        ERRORS=$((ERRORS + 1))
    fi
fi
echo ""

echo "🔐 安全检查"
echo "─────────────────────────────────────"
if [ -f ".pypirc" ]; then
    echo -e "${YELLOW}⚠️${NC} 发现 .pypirc 文件"
    if grep -q ".pypirc" ".gitignore" 2>/dev/null; then
        echo -e "${GREEN}✅${NC} .pypirc 已添加到 .gitignore"
    else
        echo -e "${RED}❌${NC} .pypirc 未添加到 .gitignore（严重安全风险！）"
        ERRORS=$((ERRORS + 1))
    fi
fi

# 检查是否有密钥泄露（排除文档和venv目录）
if grep -r "pypi-[A-Za-z0-9_-]\{40,\}" --include="*.py" --include="*.toml" --exclude-dir=venv --exclude-dir=docs . 2>/dev/null; then
    echo -e "${RED}❌${NC} 发现可能的PyPI token泄露"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅${NC} 未发现明显的密钥泄露"
fi
echo ""

echo "📦 依赖检查"
echo "─────────────────────────────────────"
if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}✅${NC} requirements.txt 存在"
    DEPS=$(wc -l < requirements.txt | tr -d ' ')
    echo "   依赖数量: $DEPS"
else
    echo -e "${RED}❌${NC} requirements.txt 缺失"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# 总结
echo "════════════════════════════════════════"
echo "📊 检查总结"
echo "════════════════════════════════════════"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}🎉 所有检查通过！可以发布到PyPI${NC}"
    echo ""
    echo "下一步："
    echo "  1. python -m build"
    echo "  2. twine check dist/*"
    echo "  3. pip install dist/*.whl  # 测试安装"
    echo "  4. twine upload dist/*     # 上传到PyPI"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  有 $WARNINGS 个警告，建议修复后再发布${NC}"
    echo ""
    echo "可以发布，但建议先解决警告"
    exit 0
else
    echo -e "${RED}❌ 有 $ERRORS 个错误和 $WARNINGS 个警告，必须修复后才能发布${NC}"
    echo ""
    echo "请修复上述错误后重新运行此脚本"
    exit 1
fi
