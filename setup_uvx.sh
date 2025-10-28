#!/bin/bash
# Mingli MCP Server 自动配置脚本 (UVX 方式)
# 使用方法: bash setup_uvx.sh

set -e

echo "🔮 Mingli MCP Server 配置脚本 (UVX 方式)"
echo "========================================="
echo ""

# 检查 uvx 是否可用
echo "📦 检查 uvx 是否已安装..."
if ! command -v uvx &> /dev/null; then
    echo "⚠️  uvx 未找到，正在尝试安装..."

    # 尝试安装 uv
    if command -v pipx &> /dev/null; then
        pipx install uv
    elif command -v pip &> /dev/null; then
        pip install uv
    elif command -v brew &> /dev/null; then
        brew install uv
    else
        echo "❌ 无法自动安装 uv，请手动安装:"
        echo "   方式1: pip install uv"
        echo "   方式2: brew install uv"
        echo "   方式3: 参考 https://docs.astral.sh/uv/getting-started/installation/"
        exit 1
    fi

    # 验证安装
    if command -v uvx &> /dev/null; then
        echo "✅ uvx 安装成功!"
    else
        echo "❌ uvx 安装失败，请手动安装"
        exit 1
    fi
else
    echo "✅ uvx 已安装"
fi

# 测试 mingli-mcp
echo ""
echo "🧪 测试 mingli-mcp 可用性..."
if timeout 10s uvx mingli-mcp &> /dev/null; then
    echo "✅ mingli-mcp 可正常启动"
else
    echo "⚠️  mingli-mcp 可能需要更新，将自动处理..."
fi

# 选择配置类型
echo ""
echo "请选择要配置的工具:"
echo "1) Cursor IDE"
echo "2) Claude Code"
echo "3) OpenAI Codex"
echo "4) 全部"
read -p "请输入选择 (1-4): " choice

case $choice in
    1)
        CLIENT="cursor"
        ;;
    2)
        CLIENT="claude"
        ;;
    3)
        CLIENT="codex"
        ;;
    4)
        CLIENT="all"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

# 配置 Cursor
if [[ "$CLIENT" == "cursor" ]] || [[ "$CLIENT" == "all" ]]; then
    echo ""
    echo "⚙️  配置 Cursor IDE..."

    CURSOR_DIR="$HOME/.cursor"
    CURSOR_CONFIG="$CURSOR_DIR/mcp.json"

    # 创建目录
    mkdir -p "$CURSOR_DIR"

    # 备份现有配置
    if [[ -f "$CURSOR_CONFIG" ]]; then
        echo "📋 备份现有配置到 $CURSOR_CONFIG.bak"
        cp "$CURSOR_CONFIG" "$CURSOR_CONFIG.bak"
    fi

    # 创建新配置
    cat > "$CURSOR_CONFIG" << 'EOF'
{
  "mcpServers": {
    "mingli": {
      "command": "uvx",
      "args": ["mingli-mcp"],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
EOF

    echo "✅ Cursor 配置已创建: $CURSOR_CONFIG"
    echo ""
    echo "📝 请重启 Cursor IDE 以加载配置"
fi

# 配置 Claude Code
if [[ "$CLIENT" == "claude" ]] || [[ "$CLIENT" == "all" ]]; then
    echo ""
    echo "⚙️  配置 Claude Code..."

    if command -v claude &> /dev/null; then
        claude mcp add mingli -- uvx mingli-mcp
        echo "✅ Claude Code 配置完成"
    else
        echo "⚠️  未检测到 Claude CLI，请手动运行:"
        echo "   claude mcp add mingli -- uvx mingli-mcp"
    fi
fi

# 配置 OpenAI Codex
if [[ "$CLIENT" == "codex" ]] || [[ "$CLIENT" == "all" ]]; then
    echo ""
    echo "⚙️  配置 OpenAI Codex..."

    if command -v codex &> /dev/null; then
        codex mcp add mingli -- uvx mingli-mcp
        echo "✅ OpenAI Codex 配置完成"
    else
        echo "⚠️  未检测到 Codex CLI，请手动运行:"
        echo "   codex mcp add mingli -- uvx mingli-mcp"
    fi
fi

# 测试配置
echo ""
echo "🧪 测试 mingli-mcp 功能..."
echo ""

# 创建一个临时测试
cat << 'EOF' | timeout 5s uvx mingli-mcp 2>&1 | head -20 || true
{}
EOF

# 完成
echo ""
echo "✨ 配置完成！"
echo "========================================="
echo ""
echo "📚 使用示例:"
echo "1. 紫微斗数排盘:"
echo "   帮我排一个紫微斗数盘：2000年8月16日，寅时，女性"
echo ""
echo "2. 八字排盘:"
echo "   帮我算八字：1985年3月15日，卯时，女性"
echo ""
echo "3. 运势查询:"
echo "   查询这个人今年的运势"
echo ""
echo "📖 完整文档: https://github.com/spyfree/mingli-mcp"
echo ""
echo "🔧 故障排除: 查看 UVX_SETUP_GUIDE.md"
echo ""
echo "🎉 享受你的命理探索之旅！"
