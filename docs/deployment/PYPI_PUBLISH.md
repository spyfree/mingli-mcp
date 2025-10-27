# PyPI 发布指南

完整的PyPI包发布流程，让你的MCP服务可以通过 `pip install` 安装。

## 📋 发布前准备清单

### ✅ 必须完成

- [x] LICENSE文件（MIT协议）
- [x] pyproject.toml配置
- [x] MANIFEST.in文件
- [ ] 更新版本号
- [ ] 完善README.md
- [ ] 添加.gitignore
- [ ] 测试代码

### 📝 需要修改的内容

#### 1. 更新 `pyproject.toml` 中的信息

```toml
[project]
name = "mingli-mcp"  # PyPI包名（需唯一）
version = "1.0.0"     # 版本号
authors = [
    {name = "Your Name", email = "your.email@example.com"}  # ⚠️ 改成你的
]

[project.urls]
Homepage = "https://github.com/yourusername/mingli-mcp"      # ⚠️ 改成你的
Repository = "https://github.com/yourusername/mingli-mcp"    # ⚠️ 改成你的
```

#### 2. 检查包名是否可用

```bash
# 访问 PyPI 搜索
# https://pypi.org/search/?q=mingli-mcp

# 如果已被占用，需要改名，比如：
# - mingli-mcp-server
# - ziwei-mcp
# - fortune-mcp
```

---

## 🔧 准备工作

### 步骤1：安装构建工具

```bash
cd /Users/lix18854/Documents/code/ziwei_mcp
source venv/bin/activate

# 安装构建和发布工具
pip install build twine wheel setuptools
```

### 步骤2：清理旧文件

```bash
# 清理之前的构建
rm -rf dist/ build/ *.egg-info
rm -rf **/__pycache__
```

### 步骤3：检查项目结构

确保目录结构正确：

```
ziwei_mcp/
├── pyproject.toml       ✅ 已创建
├── MANIFEST.in         ✅ 已创建
├── LICENSE             ✅ 已创建
├── README.md           ✅ 已有
├── mingli_mcp.py       ✅ 主入口
├── config.py           ✅
├── requirements.txt    ✅
├── core/              ✅
├── systems/           ✅
├── transports/        ✅
└── utils/             ✅
```

---

## 🏗️ 构建包

### 步骤1：本地构建

```bash
# 构建分发包
python -m build

# 会生成两个文件在 dist/ 目录：
# - mingli_mcp-1.0.0.tar.gz          (源码包)
# - mingli_mcp-1.0.0-py3-none-any.whl (wheel包)
```

### 步骤2：检查构建产物

```bash
# 查看生成的文件
ls -lh dist/

# 检查包内容
tar -tzf dist/mingli_mcp-1.0.0.tar.gz | head -20

# 检查wheel内容
unzip -l dist/mingli_mcp-1.0.0-py3-none-any.whl | head -20
```

### 步骤3：验证包元数据

```bash
# 检查包信息
twine check dist/*

# 应该输出：
# Checking dist/mingli_mcp-1.0.0.tar.gz: PASSED
# Checking dist/mingli_mcp-1.0.0-py3-none-any.whl: PASSED
```

---

## 🧪 本地测试安装

**重要**：发布前必须测试！

### 创建测试环境

```bash
# 创建新的虚拟环境
python3 -m venv test_env
source test_env/bin/activate

# 从本地wheel安装
pip install dist/mingli_mcp-1.0.0-py3-none-any.whl

# 测试命令是否可用
mingli-mcp --help
which mingli-mcp

# 测试导入
python -c "from systems import get_system; print(get_system('ziwei').get_system_name())"

# 测试运行
export TRANSPORT_TYPE=stdio
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | mingli-mcp
```

### 清理测试环境

```bash
deactivate
rm -rf test_env
```

如果测试通过，继续发布；如果失败，修复问题后重新构建。

---

## 📤 发布到PyPI

### 步骤1：注册PyPI账号

1. 访问 https://pypi.org/account/register/
2. 注册账号并验证邮箱
3. 启用2FA（两因素认证，推荐）

### 步骤2：创建API Token

1. 访问 https://pypi.org/manage/account/token/
2. 点击 "Add API token"
3. Token名称：mingli-mcp
4. Scope：Entire account（或指定项目）
5. 复制生成的token（以 `pypi-` 开头）

### 步骤3：配置认证

创建 `~/.pypirc` 文件：

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-token-here
```

**安全提示**：
```bash
chmod 600 ~/.pypirc  # 限制文件权限
```

### 步骤4：上传到测试PyPI（可选但推荐）

```bash
# 注册测试PyPI账号（https://test.pypi.org）
# 创建测试token

# 上传到测试PyPI
twine upload --repository testpypi dist/*

# 测试安装
pip install --index-url https://test.pypi.org/simple/ mingli-mcp
```

### 步骤5：上传到正式PyPI

```bash
# 上传到PyPI
twine upload dist/*

# 输出类似：
# Uploading distributions to https://upload.pypi.org/legacy/
# Uploading mingli_mcp-1.0.0-py3-none-any.whl
# 100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Uploading mingli_mcp-1.0.0.tar.gz
# 100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# View at:
# https://pypi.org/project/mingli-mcp/1.0.0/
```

---

## 🎯 在Coze中使用

发布成功后，在Coze配置：

### 方法1：使用uvx（推荐）

```json
{
  "mcpServers": {
    "mingli": {
      "command": "uvx",
      "args": ["mingli-mcp@1.0.0"],
      "env": {
        "TRANSPORT_TYPE": "stdio",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 方法2：使用pip

```json
{
  "mcpServers": {
    "mingli": {
      "command": "python",
      "args": ["-m", "pip", "install", "mingli-mcp==1.0.0", "&&", "mingli-mcp"],
      "env": {}
    }
  }
}
```

### 方法3：使用pipx

```json
{
  "mcpServers": {
    "mingli": {
      "command": "pipx",
      "args": ["run", "mingli-mcp@1.0.0"],
      "env": {}
    }
  }
}
```

---

## 🔄 版本更新流程

### 更新版本号

编辑 `pyproject.toml`：

```toml
[project]
version = "1.0.1"  # 增加版本号
```

### 版本号规范（语义化版本）

- **主版本号（Major）**: 不兼容的API变更
- **次版本号（Minor）**: 向下兼容的功能新增
- **修订号（Patch）**: 向下兼容的问题修正

示例：
- `1.0.0` → `1.0.1`：Bug修复
- `1.0.0` → `1.1.0`：新增功能
- `1.0.0` → `2.0.0`：重大变更

### 发布新版本

```bash
# 1. 更新版本号
# 编辑 pyproject.toml

# 2. 清理旧构建
rm -rf dist/ build/ *.egg-info

# 3. 重新构建
python -m build

# 4. 测试安装
pip install dist/*.whl --force-reinstall

# 5. 上传新版本
twine upload dist/*
```

---

## 📊 发布后检查

### 验证PyPI页面

访问：https://pypi.org/project/mingli-mcp/

检查：
- [ ] 项目描述正确
- [ ] README显示正常
- [ ] 链接有效
- [ ] 依赖列表完整
- [ ] License显示

### 测试安装

```bash
# 新环境测试
python3 -m venv fresh_test
source fresh_test/bin/activate

# 从PyPI安装
pip install mingli-mcp

# 测试运行
mingli-mcp --help

deactivate
rm -rf fresh_test
```

### 更新文档

在README.md添加安装说明：

```markdown
## 安装

### 从PyPI安装

\`\`\`bash
pip install mingli-mcp
\`\`\`

### 使用

\`\`\`bash
mingli-mcp
\`\`\`
```

---

## 🚨 常见问题

### Q1: 包名已被占用

**解决**：
```bash
# 改名，在 pyproject.toml 中修改
name = "mingli-mcp-server"  # 或其他名称
```

### Q2: 上传失败 - 403 Forbidden

**原因**：Token无效或权限不足

**解决**：
1. 检查 `~/.pypirc` 中的token
2. 确认token有上传权限
3. 重新生成token

### Q3: wheel构建失败

**检查**：
```bash
# 查看详细错误
python -m build --verbose

# 检查setup配置
python -c "import setuptools; print(setuptools.__version__)"
```

### Q4: 依赖安装失败

**原因**：requirements.txt中的依赖无法安装

**解决**：
```toml
# 在 pyproject.toml 中指定兼容版本
dependencies = [
    "py-iztro>=0.1.5",
    "lunar_python>=1.4.0",  # 降低版本要求
    ...
]
```

---

## 🔐 安全建议

### 1. 保护API Token

```bash
# 不要提交到Git
echo ".pypirc" >> .gitignore

# 使用环境变量
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-token

# 上传时无需配置文件
twine upload dist/*
```

### 2. 签名发布

```bash
# 安装GPG
brew install gnupg

# 生成密钥
gpg --gen-key

# 签名并上传
twine upload --sign dist/*
```

### 3. 启用2FA

在PyPI账号设置中启用两因素认证。

---

## 📈 推广和维护

### 添加Badge

在README.md添加：

```markdown
[![PyPI version](https://badge.fury.io/py/mingli-mcp.svg)](https://badge.fury.io/py/mingli-mcp)
[![Downloads](https://pepy.tech/badge/mingli-mcp)](https://pepy.tech/project/mingli-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

### 监控下载量

- PyPI Stats: https://pypistats.org/packages/mingli-mcp
- Libraries.io: https://libraries.io/pypi/mingli-mcp

### 收集反馈

- 在GitHub创建Issues
- 监控PyPI评论
- 建立用户交流群

---

## ✅ 发布前最终检查清单

- [ ] 代码测试通过
- [ ] 版本号正确
- [ ] README完整
- [ ] LICENSE存在
- [ ] 依赖版本合理
- [ ] 本地安装测试通过
- [ ] .gitignore配置正确
- [ ] 个人信息已更新（authors, urls）
- [ ] 包名在PyPI可用
- [ ] API token已配置

---

## 📚 参考资源

- [Python Packaging User Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [PEP 517 - Build System](https://peps.python.org/pep-0517/)

---

**准备好发布了吗？运行快速检查脚本：**

```bash
./scripts/check_ready_to_publish.sh
```
