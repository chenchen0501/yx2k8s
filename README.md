<h1 align="center">yx2k8s</h1>

<p align="center">
  <strong>YunXiao to Kubernetes Auto Deploy Tool</strong>
</p>

<p align="center">
  云效到 K8s 自动部署工具 | 基于浏览器自动化的 CI/CD 解决方案
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python"></a>
  <a href="https://playwright.dev/"><img src="https://img.shields.io/badge/Playwright-1.48.0-green.svg" alt="Playwright"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"></a>
  <a href="https://github.com/your-username/yx2k8s/stargazers"><img src="https://img.shields.io/github/stars/your-username/yx2k8s?style=social" alt="GitHub stars"></a>
</p>

---

**yx2k8s** (YunXiao to K8s) 是一个基于 Playwright 的浏览器自动化工具,无需 API 权限即可实现从云效 Flow 构建到 Kubernetes 部署的全自动化流程。

## ✨ 特性

- 🚀 **零 API 依赖** - 仅需 Web 控制台访问权限
- 🤖 **全自动化** - 一键触发构建并更新 K8s 部署
- 🔐 **登录状态管理** - 首次手动登录,后续自动运行
- 🎯 **精准版本追踪** - 自动从构建日志提取镜像版本号
- 📸 **完整日志与截图** - 失败时自动保存现场
- 🌍 **多环境支持** - 前端/后端 × 测试/生产共 4 种环境
- 🎛️ **Web 界面** - 可视化操作界面,支持任务多选和实时日志
- ⚡ **快速部署** - 5 分钟即可上手使用

## 🎬 快速预览

### 方式一: Web 界面(推荐)

```bash
# 安装
pip install -r requirements.txt
playwright install chromium

# 配置
cp .env.example .env
vim .env

# 启动 Web 服务
python web_server.py

# 访问 http://localhost:5001
# 选择需要部署的环境并点击【开始部署】
```

### 方式二: 命令行

```bash
# 运行(使用默认配置)
python main.py
```

就是这么简单! ✨

---

## 📑 目录

- [✨ 特性](#-特性)
- [🎬 快速预览](#-快速预览)
- [🎯 项目背景](#-项目背景)
- [💡 解决方案](#-解决方案)
- [📋 核心功能](#-核心功能)
- [🌟 适用场景](#-适用场景)
- [⚙️ 环境要求](#️-环境要求)
- [🚀 快速开始](#-快速开始)
- [📂 项目结构](#-项目结构)
- [🔧 配置说明](#-配置说明)
- [🎯 工作流程](#-工作流程)
- [📊 运行示例](#-运行示例)
- [❓ 常见问题](#-常见问题)
- [🔐 安全说明](#-安全说明)
- [📝 维护与扩展](#-维护与扩展)
- [🛣️ Roadmap](#️-roadmap)
- [🤝 贡献指南](#-贡献指南)
- [📞 支持与反馈](#-支持与反馈)
- [📄 许可证](#-许可证)
- [⚠️ 免责声明](#️-免责声明)
- [🙏 致谢](#-致谢)

---

## 🎯 项目背景

在现代 DevOps 实践中,常见的 CI/CD 流程通常是:

```
代码提交 → CI 构建 → 推送镜像 → K8s 部署
```

然而,某些场景下可能面临以下限制:

1. **API 访问受限**: 云效 API 或 K8s API 可能受到网络、权限等限制
2. **合规要求**: 某些企业规定只能通过 Web 控制台操作,不允许直接调用 API
3. **临时方案**: 需要快速实现自动化,但暂时无法打通 API 调用链路
4. **权限隔离**: 开发人员只有控制台访问权限,没有 API Token

在这些情况下,传统的 API 自动化方案无法使用,但手动操作又繁琐且容易出错。

## 💡 解决方案

本工具通过 **浏览器自动化技术**,模拟真人操作 Web 控制台,实现:

- ✅ **无需 API 权限**: 只要能访问 Web 控制台即可
- ✅ **符合合规要求**: 全程通过浏览器操作,与人工点击无异
- ✅ **复用登录状态**: 首次手动登录后,后续自动运行
- ✅ **可视化执行**: 可选择显示浏览器窗口,方便调试和监控
- ✅ **完整日志**: 详细记录每个操作步骤,失败时自动截图

## 📋 核心功能

### 1. **云效构建触发与监控**

- 自动点击【运行】按钮触发 Pipeline 构建
- 实时监控构建状态,等待构建完成
- 从构建日志中提取最新镜像版本号

### 2. **K8s 镜像版本更新**

- 自动访问 Deployment 详情页
- 点击【调整镜像版本】按钮
- 填入新版本号并确认更新

### 3. **登录状态管理**

- 首次手动登录,自动保存 Cookie
- 后续运行自动复用登录状态
- 支持多账号切换

### 4. **异常处理与调试**

- 失败时自动截图,保存到 `screenshots/` 目录
- 详细的日志输出,便于排查问题
- 支持自定义超时时间

---

## 🌟 适用场景

本工具特别适合以下场景:

- 🏢 **企业内部自动化**: 仅有 Web 控制台权限,无 API Token
- 🔒 **合规要求严格**: 必须通过 Web 操作,留下审计日志
- 🚀 **快速原型验证**: 快速实现自动化,无需等待 API 对接
- 🔧 **临时过渡方案**: 在 API 方案完成前的临时替代
- 🎓 **学习浏览器自动化**: Playwright 的实战示例

## ⚙️ 环境要求

- **操作系统**: macOS / Windows / Linux
- **Python 版本**: 3.8+
- **网络要求**:
  - 能访问云效公网地址 (https://flow.aliyun.com)
  - 能访问 K8s 控制台 (可能需要 VPN)

---

## 🚀 快速开始

### 1. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件,填入你的实际配置
vim .env  # 或使用其他编辑器
```

**`.env` 配置说明:**

```bash
# 前端测试环境
FRONTEND_TEST_YUNXIAO_URL=https://flow.aliyun.com/pipelines/YOUR_PIPELINE_ID/current
FRONTEND_TEST_K8S_URL=https://k8s.dev.your-domain.com:40022/...

# 前端生产环境
FRONTEND_PROD_YUNXIAO_URL=https://flow.aliyun.com/pipelines/YOUR_PIPELINE_ID/current
FRONTEND_PROD_K8S_URL=https://k8s.prod.your-domain.com:40022/...

# 后端配置(预留)
BACKEND_TEST_YUNXIAO_URL=
BACKEND_PROD_YUNXIAO_URL=
```

### 2. 安装依赖

```bash
# 进入项目目录
cd yx2k8s

# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器驱动
playwright install chromium
```

### 3. 首次运行

```bash
python main.py
```

**⚠️ 首次运行需要手动登录:**

1. 脚本会自动打开浏览器
2. 访问云效页面时,请手动登录
3. 访问 K8s 控制台时,请手动登录
4. 登录成功后,脚本会自动保存登录状态到 `auth.json`
5. 后续运行将自动复用登录状态,无需再次登录

### 4. 后续运行(全自动)

```bash
python main.py
```

后续运行会自动完成所有步骤,无需人工干预!

---

## 📂 项目结构

```
yx2k8s/
├── main.py                   # 主程序入口
├── config.py                 # 配置管理
├── yunxiao.py                # 云效操作模块
├── k8s.py                    # K8s 操作模块
├── utils.py                  # 工具函数(日志、截图)
├── requirements.txt          # Python 依赖
├── .env                      # 环境变量配置(需自行创建)
├── .env.example              # 环境变量模板
├── auth.json                 # 登录状态存储(自动生成)
├── screenshots/              # 失败时的截图
├── logs/                     # 日志目录(预留)
├── LICENSE                   # MIT 许可证
├── CHANGELOG.md              # 版本变更日志
├── CONTRIBUTING.md           # 贡献指南
├── OPEN_SOURCE_CHECKLIST.md  # 开源检查清单
└── README.md                 # 本文档
```

---

## 🔧 配置说明

### 环境变量配置 (`.env` 文件)

**前端配置:**

```bash
# 测试环境
FRONTEND_TEST_YUNXIAO_URL=https://flow.aliyun.com/pipelines/4368447/current
FRONTEND_TEST_K8S_URL=https://k8s.dev.wuxi.epartical.com:40022/...
FRONTEND_TEST_TAG_PATTERN=javaly/jpms-web:(dev-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})

# 生产环境
FRONTEND_PROD_YUNXIAO_URL=https://flow.aliyun.com/pipelines/YOUR_PROD_ID/current
FRONTEND_PROD_K8S_URL=https://k8s.prod.wuxi.epartical.com:40022/...
FRONTEND_PROD_TAG_PATTERN=javaly/jpms-web:(prod-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})
```

**后端配置(预留):**

```bash
BACKEND_TEST_YUNXIAO_URL=
BACKEND_TEST_K8S_URL=
BACKEND_PROD_YUNXIAO_URL=
BACKEND_PROD_K8S_URL=
```

### 代码配置 (`config.py`)

### 超时配置

```python
BUILD_TIMEOUT = 300000      # 构建超时 5 分钟
OPERATION_TIMEOUT = 30000   # 操作超时 30 秒
PAGE_LOAD_TIMEOUT = 60000   # 页面加载超时 1 分钟
```

### 浏览器配置

```python
HEADLESS = False  # 是否无头模式(True=后台运行, False=显示浏览器)
SCREENSHOT_ON_ERROR = True  # 失败时自动截图
```

---

## 🎯 工作流程

### 完整流程:

```
┌─────────────────────────────────────────┐
│  云效部分 (约 5-10 分钟)                 │
├─────────────────────────────────────────┤
│  1. 访问 Pipeline 页面                   │
│  2. 点击【运行】按钮                      │
│  3. 确认运行配置                         │
│  4. 等待构建完成                         │
│  5. 打开构建日志                         │
│  6. 提取版本号                           │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  K8s 部分 (约 10 秒)                     │
├─────────────────────────────────────────┤
│  1. 访问 Deployment 详情页               │
│  2. 点击【调整镜像版本】                  │
│  3. 填入新版本号                         │
│  4. 确认更新                             │
└─────────────────────────────────────────┘
```

---

## 📊 运行示例

```bash
$ python main.py

============================================================
云效到 K8s 镜像版本自动更新工具
============================================================
[2025-11-12 14:22:30] ℹ️ 启动浏览器 (无头模式: False)...
[2025-11-12 14:22:31] ℹ️ 检测到登录状态文件: auth.json

【步骤 1/2】云效: 触发构建并获取镜像版本号
------------------------------------------------------------
[2025-11-12 14:22:32] ▶️ 访问云效 Pipeline 页面...
[2025-11-12 14:22:35] ▶️ 点击【运行】按钮...
[2025-11-12 14:22:36] ▶️ 确认运行配置...
[2025-11-12 14:22:37] ⏳ 等待构建完成(最长5分钟)...
[2025-11-12 14:27:42] ✅ 构建已完成
[2025-11-12 14:27:43] ▶️ 打开构建日志...
[2025-11-12 14:27:45] ▶️ 展开镜像构建日志...
[2025-11-12 14:27:48] ✅ 成功获取版本号: dev-2025-11-12-14-20-32
------------------------------------------------------------
[2025-11-12 14:27:48] ✅ 【步骤 1/2】完成! 版本号: dev-2025-11-12-14-20-32

【步骤 2/2】K8s: 更新 Deployment 镜像版本
------------------------------------------------------------
[2025-11-12 14:27:49] ▶️ 访问 K8s Deployment 页面...
[2025-11-12 14:27:52] ▶️ 点击【调整镜像版本】按钮...
[2025-11-12 14:27:53] ℹ️ 调整镜像版本弹窗已打开
[2025-11-12 14:27:53] ▶️ 填入新版本号: dev-2025-11-12-14-20-32
[2025-11-12 14:27:54] ✅ 已填入新版本: dev-2025-11-12-14-20-32
[2025-11-12 14:27:54] ▶️ 点击【确定】按钮...
[2025-11-12 14:27:56] ✅ 镜像版本更新成功!
------------------------------------------------------------
[2025-11-12 14:27:56] ✅ 【步骤 2/2】完成!
[2025-11-12 14:27:56] ℹ️ 登录状态已保存到: auth.json

============================================================
[2025-11-12 14:27:56] ✅ 🎉 任务全部完成! 耗时: 5分26秒
============================================================
```

---

## ❓ 常见问题

### 1. 首次运行需要登录吗?

是的,首次运行需要手动登录云效和 K8s 控制台。登录后,脚本会自动保存登录状态到 `auth.json`,后续运行无需再次登录。

### 2. 如何切换账号?

删除 `auth.json` 文件,再次运行脚本即可手动登录新账号。

```bash
rm auth.json
python main.py
```

### 3. 构建超时怎么办?

默认构建超时时间是 5 分钟,如果构建时间较长,可以在 `config.py` 中调整:

```python
BUILD_TIMEOUT = 600000  # 改为 10 分钟
```

### 4. 失败时如何排查?

脚本失败时会自动截图保存到 `screenshots/` 目录,文件名包含时间戳和错误类型,例如:

```
screenshots/yunxiao_timeout_20251112_142530.png
screenshots/k8s_error_20251112_142530.png
```

### 5. 如何后台运行?

在 `config.py` 中设置:

```python
HEADLESS = True  # 开启无头模式
```

### 6. 支持多个 Deployment 吗?

当前版本仅支持单个 Deployment。如需支持多个,可以修改 `config.py` 添加配置列表,然后在 `main.py` 中循环调用。

### 7. 如何自定义 URL?

修改 `config.py` 中的 `YUNXIAO_URL` 和 `K8S_URL` 即可。

---

## 🔐 安全说明

- 全程本地执行,不上传任何数据
- 不保存账号密码,仅复用浏览器 Cookie
- 不调用云效 API 和 K8s API,仅模拟浏览器操作
- `auth.json` 文件包含登录凭证,请妥善保管
- `.env` 文件包含敏感 URL,已添加到 `.gitignore`,不会提交到仓库

---

## 📝 维护与扩展

### 控制台页面改版怎么办?

如果云效或 K8s 控制台改版导致元素定位失败,只需要:

1. 更新 `yunxiao.py` 或 `k8s.py` 中的元素定位器
2. 无需改动整体流程逻辑

### 如何支持多环境?

项目已支持前端/后端、测试/生产多环境配置,通过 `.env` 文件管理:

```bash
# 前端测试环境
FRONTEND_TEST_YUNXIAO_URL=...
FRONTEND_TEST_K8S_URL=...

# 前端生产环境
FRONTEND_PROD_YUNXIAO_URL=...
FRONTEND_PROD_K8S_URL=...

# 后端测试环境(预留)
BACKEND_TEST_YUNXIAO_URL=...
BACKEND_TEST_K8S_URL=...

# 后端生产环境(预留)
BACKEND_PROD_YUNXIAO_URL=...
BACKEND_PROD_K8S_URL=...
```

在代码中通过 `config.FRONTEND_CONFIG['test']` 或 `config.FRONTEND_CONFIG['prod']` 访问对应环境配置。

---

## 🛣️ Roadmap

- [ ] 支持命令行参数选择环境 (`--env prod`)
- [ ] 支持批量更新多个 Deployment
- [ ] 支持 Helm Chart 更新
- [ ] 增加 Web UI 界面
- [ ] 支持更多 CI/CD 平台 (Jenkins, GitLab CI 等)
- [ ] 支持更多 K8s 管理平台 (Rancher, KubeSphere 等)
- [ ] 增加钉钉/企业微信通知

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request!

### 如何贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: 添加某个功能'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

### 开发规范

- 遵循 PEP 8 代码规范
- 添加必要的注释和文档
- 更新 README 和 CHANGELOG

---

## 📞 支持与反馈

- **Issue**: [GitHub Issues](https://github.com/your-username/yx2k8s/issues)
- **讨论**: [GitHub Discussions](https://github.com/your-username/yx2k8s/discussions)
- **Star 项目**: 如果觉得有帮助,欢迎 [Star ⭐️](https://github.com/your-username/yx2k8s)

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

---

## ⚠️ 免责声明

- 本工具仅用于自动化日常运维操作,请勿用于非法用途
- 使用本工具产生的任何后果由使用者自行承担
- 建议在非生产环境充分测试后再用于生产环境
- 请遵守所在企业的安全规范和操作流程

---

## 🙏 致谢

- [Playwright](https://playwright.dev/) - 强大的浏览器自动化框架
- [python-dotenv](https://github.com/theskumar/python-dotenv) - 环境变量管理
- 所有贡献者和使用者

---

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/your-username">@your-username</a>
</p>

<p align="center">
  <strong>祝使用愉快! 🎉</strong>
</p>

<p align="center">
  如果觉得有帮助,欢迎 <a href="https://github.com/your-username/yx2k8s">Star ⭐️</a>
</p>
