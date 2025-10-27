# PyPI 发布快速指南（5分钟版）

**在正式发布前**，你需要先修改这些信息：

## ⚠️ 必须修改

打开 `pyproject.toml`，修改以下内容：

```toml
[project]
name = "mingli-mcp"  # 如果名字被占用，改成其他的
authors = [
    {name = "你的名字", email = "你的邮箱@example.com"}  # ← 改这里
]

[project.urls]
Homepage = "https://github.com/你的用户名/mingli-mcp"      # ← 改这里
Repository = "https://github.com/你的用户名/mingli-mcp"    # ← 改这里
```

## 🚀 快速发布步骤

### 1. 安装工具（已完成✅）

```bash
pip install build twine
```

### 2. 检查准备情况

```bash
./scripts/check_ready_to_publish.sh
```

应该显示"所有检查通过"。

### 3. 构建包

```bash
# 清理旧文件
rm -rf dist/ build/ *.egg-info

# 构建
python -m build
```

会生成 `dist/` 目录，包含两个文件：
- `mingli_mcp-1.0.0.tar.gz`
- `mingli_mcp-1.0.0-py3-none-any.whl`

### 4. 本地测试

```bash
# 创建测试环境
python3 -m venv test_env
source test_env/bin/activate

# 安装测试
pip install dist/mingli_mcp-1.0.0-py3-none-any.whl

# 测试命令
mingli-mcp --help

# 清理
deactivate
rm -rf test_env
```

### 5. 上传到PyPI

#### A. 注册PyPI账号
1. 访问 https://pypi.org/account/register/
2. 注册并验证邮箱

#### B. 创建API Token
1. 访问 https://pypi.org/manage/account/token/
2. 创建token（选择"Entire account"）
3. 复制token（以 `pypi-` 开头）

#### C. 上传

```bash
# 方式1：直接上传（会提示输入用户名和密码）
twine upload dist/*
# 用户名: __token__
# 密码: 你的token

# 方式2：使用环境变量
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-你的token
twine upload dist/*
```

### 6. 验证

访问 https://pypi.org/project/mingli-mcp/

测试安装：
```bash
pip install mingli-mcp
mingli-mcp --help
```

## 🎯 在Coze使用

```json
{
  "mcpServers": {
    "mingli": {
      "command": "uvx",
      "args": ["mingli-mcp@1.0.0"]
    }
  }
}
```

## ⚠️ 注意事项

1. **包名唯一性**：在 https://pypi.org/search/ 搜索，确保名字未被占用
2. **版本号不可重复**：同一版本号只能上传一次
3. **无法删除**：PyPI不允许删除已发布的包（只能隐藏）
4. **先测试后发布**：建议先上传到 test.pypi.org 测试

## 🔄 更新版本

1. 修改 `pyproject.toml` 中的 `version = "1.0.1"`
2. 重新构建和上传

```bash
rm -rf dist/
python -m build
twine upload dist/*
```

## 📞 遇到问题？

参考完整文档：`PYPI_PUBLISH.md`
