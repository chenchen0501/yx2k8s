# 贡献指南

感谢你考虑为本项目做出贡献!

## 📋 行为准则

本项目遵循 [贡献者公约](https://www.contributor-covenant.org/zh-cn/version/2/1/code_of_conduct/)。参与本项目即表示你同意遵守其条款。

## 🚀 如何贡献

### 报告 Bug

如果你发现了 Bug,请:

1. 检查 [Issues](https://github.com/your-username/yx2k8s/issues) 确保 Bug 尚未被报告
2. 使用 [Bug 报告模板](.github/ISSUE_TEMPLATE/bug_report.md) 创建新 Issue
3. 提供详细的复现步骤、环境信息和错误日志
4. 如果可能,附上截图

### 提出功能需求

如果你有新功能的想法,请:

1. 检查 [Issues](https://github.com/your-username/yx2k8s/issues) 确保功能尚未被提出
2. 使用 [功能需求模板](.github/ISSUE_TEMPLATE/feature_request.md) 创建新 Issue
3. 清晰描述功能和使用场景
4. 说明为什么这个功能对项目有价值

### 提交 Pull Request

#### 前置条件

- Python 3.8+
- Git
- 熟悉 Playwright

#### 开发流程

1. **Fork 仓库**

   点击右上角的 "Fork" 按钮

2. **克隆仓库**

   ```bash
   git clone https://github.com/your-username/yx2k8s.git
   cd yx2k8s
   ```

3. **创建特性分支**

   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

4. **安装依赖**

   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

5. **配置环境**

   ```bash
   cp .env.example .env
   # 编辑 .env 填入你的测试配置
   ```

6. **进行开发**

   - 编写代码
   - 添加必要的注释
   - 遵循代码规范

7. **测试变更**

   ```bash
   # 运行完整测试
   python main.py

   # 确保没有破坏现有功能
   ```

8. **提交变更**

   ```bash
   git add .
   git commit -m "feat: 添加某个功能"
   ```

   提交信息格式:
   - `feat:` 新功能
   - `fix:` Bug 修复
   - `docs:` 文档更新
   - `style:` 代码格式调整
   - `refactor:` 代码重构
   - `perf:` 性能优化
   - `test:` 测试相关
   - `chore:` 构建过程或辅助工具变动

9. **推送到 Fork 仓库**

   ```bash
   git push origin feature/your-feature-name
   ```

10. **创建 Pull Request**

    - 访问你的 Fork 仓库
    - 点击 "New Pull Request"
    - 填写 PR 描述
    - 等待 Review

## 📝 代码规范

### Python 代码规范

- 遵循 [PEP 8](https://peps.python.org/pep-0008/) 规范
- 使用 4 个空格缩进
- 每行代码不超过 100 字符
- 函数和类添加 docstring
- 重要逻辑添加注释

示例:

```python
def extract_version_tag(log_text: str, pattern: str) -> str:
    """
    从日志文本中提取版本号

    Args:
        log_text: 日志文本内容
        pattern: 正则表达式模式

    Returns:
        str: 提取的版本号

    Raises:
        ValueError: 未找到版本号时抛出
    """
    match = re.search(pattern, log_text)
    if not match:
        raise ValueError("未找到版本号")
    return match.group(1)
```

### 文件组织

```
yx2k8s/
├── main.py              # 主程序入口
├── config.py            # 配置管理
├── yunxiao.py           # 云效操作模块
├── k8s.py               # K8s 操作模块
├── utils.py             # 工具函数
├── requirements.txt     # 依赖列表
├── .env.example         # 环境变量模板
├── README.md            # 项目文档
├── CONTRIBUTING.md      # 贡献指南
├── CHANGELOG.md         # 变更日志
└── LICENSE              # 许可证
```

### Git 提交规范

提交信息格式:

```
<type>(<scope>): <subject>

<body>

<footer>
```

示例:

```
feat(k8s): 添加批量更新 Deployment 功能

- 支持从配置文件读取多个 Deployment
- 支持并发更新
- 添加进度显示

Closes #123
```

## 🔍 Review 流程

1. **自动检查**: CI 会自动运行测试和代码检查
2. **人工 Review**: 维护者会审查代码质量和逻辑
3. **修改建议**: 根据 Review 意见修改代码
4. **合并**: 所有检查通过后,PR 将被合并

## 📚 开发资源

### 文档

- [Playwright 文档](https://playwright.dev/python/)
- [Python-dotenv 文档](https://github.com/theskumar/python-dotenv)
- [云效文档](https://help.aliyun.com/product/153741.html)

### 工具推荐

- **IDE**: VS Code / PyCharm
- **代码格式化**: black, autopep8
- **代码检查**: pylint, flake8
- **类型检查**: mypy

## ❓ 常见问题

### Q: 如何调试代码?

设置 `HEADLESS = False` 可以看到浏览器操作过程。

### Q: 如何添加新的 CI/CD 平台支持?

参考 `yunxiao.py` 的实现,创建新的模块文件。

### Q: 如何处理登录失败?

确保首次运行时手动完成登录,工具会自动保存登录状态。

## 💬 讨论

有任何问题或建议,欢迎在 [Discussions](https://github.com/your-username/yx2k8s/discussions) 中讨论。

## 🙏 感谢

感谢所有贡献者的付出! 🎉

---

**开始贡献前,建议先阅读本指南和 [README.md](README.md)。**
