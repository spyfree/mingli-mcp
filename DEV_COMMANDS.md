# 开发命令快速参考

## 🚀 快速开始

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装开发依赖
pip install -e ".[dev]"
```

## 🧪 测试

```bash
# 运行所有测试
pytest

# 详细输出
pytest -v

# 测试覆盖率
pytest --cov=. --cov-report=term-missing --cov-report=html

# 查看HTML覆盖率报告
open htmlcov/index.html

# 运行特定测试文件
pytest tests/test_bazi.py

# 运行特定测试函数
pytest tests/test_bazi.py::test_bazi_chart
```

## 🎨 代码格式化

```bash
# 检查代码格式（不修改）
black --check .

# 自动格式化代码
black .

# 格式化特定文件
black mingli_mcp
```

## 📦 导入排序

```bash
# 检查导入顺序
isort --check-only .

# 自动修复导入顺序
isort .

# 显示差异
isort --diff .
```

## 🔍 代码检查

```bash
# 运行flake8
flake8 .

# 显示统计信息
flake8 . --count --statistics

# 检查特定文件
flake8 mingli_mcp

# 运行mypy类型检查
mypy .

# 运行pylint
pylint mingli_mcp
```

## 🔧 一键质量检查

```bash
# 运行所有质量检查
black --check . && isort --check-only . && flake8 . && pytest
```

## 📦 构建和发布

```bash
# 构建包
python -m build

# 检查包
twine check dist/*

# 测试发布（需要配置）
twine upload --repository testpypi dist/*

# 正式发布
twine upload dist/*
```

## 🐛 调试

```bash
# 运行服务器（stdio模式）
python -m mingli_mcp

# 运行服务器（HTTP模式）
TRANSPORT_TYPE=http HTTP_PORT=8080 python -m mingli_mcp

# 查看日志（调试级别）
LOG_LEVEL=DEBUG python -m mingli_mcp
```

## 🧹 清理

```bash
# 清理构建文件
rm -rf build/ dist/ *.egg-info

# 清理缓存
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# 清理测试和覆盖率文件
rm -rf .pytest_cache htmlcov .coverage
```

## 🔄 Git工作流

```bash
# 查看状态
git status

# 查看改动
git diff

# 添加所有改动
git add .

# 提交（注意格式）
git commit -m "Fix: 改进异常处理机制"

# 推送
git push
```

## 💡 提示

### 提交前检查清单
```bash
# 1. 运行测试
pytest

# 2. 格式化代码
black . && isort .

# 3. 检查代码质量
flake8 .

# 4. 查看改动
git diff

# 5. 提交
git add .
git commit -m "Your message"
```

### VS Code 任务
可以在 `.vscode/tasks.json` 中配置快捷任务：
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Run Tests",
      "type": "shell",
      "command": "pytest -v"
    },
    {
      "label": "Format Code",
      "type": "shell",
      "command": "black . && isort ."
    },
    {
      "label": "Quality Check",
      "type": "shell",
      "command": "black --check . && flake8 ."
    }
  ]
}
```

### 环境变量
创建 `.env` 文件：
```bash
LOG_LEVEL=INFO
TRANSPORT_TYPE=stdio
MCP_SERVER_NAME=ziwei_mcp
```

### 预提交钩子 (可选)
创建 `.git/hooks/pre-commit`：
```bash
#!/bin/bash
black --check . || exit 1
isort --check-only . || exit 1
flake8 . || exit 1
pytest || exit 1
```

然后：
```bash
chmod +x .git/hooks/pre-commit
```
