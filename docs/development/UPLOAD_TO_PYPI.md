# 上传到PyPI - 最后一步！

包已经构建好了，只需要你的PyPI token就可以发布！

## 📋 准备工作（5分钟）

### 步骤1：注册PyPI账号

1. 访问：https://pypi.org/account/register/
2. 填写信息并注册
3. 验证邮箱

### 步骤2：创建API Token

1. 登录PyPI后，访问：https://pypi.org/manage/account/token/
2. 点击 **"Add API token"**
3. Token name: `mingli-mcp`
4. Scope: **Entire account** （或者上传后选择 Project: mingli-mcp）
5. 点击 **"Create token"**
6. **重要**：复制生成的token（以 `pypi-` 开头的长字符串）

⚠️ **注意**：Token只显示一次，请立即保存！

---

## 🚀 上传到PyPI

在终端执行：

\`\`\`bash
cd /Users/lix18854/Documents/code/ziwei_mcp
source venv/bin/activate

# 上传（会提示输入用户名和密码）
twine upload dist/*
\`\`\`

**提示输入时：**
- Username: `__token__`
- Password: `粘贴你的PyPI token`

或者使用环境变量：

\`\`\`bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-你的token这里

twine upload dist/*
\`\`\`

---

## ✅ 验证发布

上传成功后：

1. **访问PyPI页面**
   https://pypi.org/project/mingli-mcp/

2. **测试安装**
   \`\`\`bash
   # 新建测试环境
   python3 -m venv test_install
   source test_install/bin/activate
   
   # 从PyPI安装
   pip install mingli-mcp
   
   # 测试命令
   mingli-mcp --help
   
   # 清理
   deactivate
   rm -rf test_install
   \`\`\`

---

## 🎯 在Coze使用

发布成功后，在Coze配置：

\`\`\`json
{
  "mcpServers": {
    "mingli": {
      "command": "uvx",
      "args": ["mingli-mcp@1.0.0"],
      "env": {
        "TRANSPORT_TYPE": "stdio"
      }
    }
  }
}
\`\`\`

或使用pipx：

\`\`\`json
{
  "mcpServers": {
    "mingli": {
      "command": "pipx",
      "args": ["run", "mingli-mcp@1.0.0"]
    }
  }
}
\`\`\`

---

## 🔄 更新版本

以后更新版本时：

1. 修改 `pyproject.toml` 中的版本号
   \`\`\`toml
   version = "1.0.1"
   \`\`\`

2. 提交到Git
   \`\`\`bash
   git add pyproject.toml
   git commit -m "Bump version to 1.0.1"
   git push
   \`\`\`

3. 重新构建和上传
   \`\`\`bash
   rm -rf dist/
   python -m build
   twine upload dist/*
   \`\`\`

---

## 🐛 常见问题

### Q: 上传失败 - 403 Forbidden
**A**: Token无效或没有权限，重新生成token

### Q: 包名已存在
**A**: 修改 `pyproject.toml` 中的 `name`，改成如 `mingli-mcp-spyfree`

### Q: 版本号已存在
**A**: PyPI不允许重复版本号，增加版本号再上传

---

## 📞 需要帮助？

- PyPI文档：https://pypi.org/help/
- Twine文档：https://twine.readthedocs.io/

---

**🎉 准备好了！运行 `twine upload dist/*` 即可发布！**
