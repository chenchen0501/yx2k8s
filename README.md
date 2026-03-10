# yx2k8s - 云效 K8s 自动部署工具

> 基于浏览器自动化的 CI/CD 解决方案，无需 API 权限即可实现从云效 Flow 构建到 Kubernetes 部署的全自动化流程。

## ✨ 特性

- 🚀 **零 API 依赖** - 仅需 Web 控制台访问权限
- 🤖 **全自动化** - 一键触发构建并更新 K8s 部署
- 🔐 **登录状态管理** - 首次手动登录，后续自动运行
- 🎯 **精准版本追踪** - 自动从构建日志提取镜像版本号
- 📸 **完整日志与截图** - 失败时自动保存现场
- 🎛️ **Web 界面** - 可视化操作界面，支持实时日志
- ⚡ **快速部署** - 5 分钟即可上手使用

## 🎬 快速开始

### 1. 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器驱动
playwright install chromium

# 安装前端依赖
cd web
npm install
cd ..
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的实际配置
vim .env
```

**`.env` 配置说明:**

```bash
# 前端配置
FRONTEND_TEST_YUNXIAO_URL=https://flow.aliyun.com/pipelines/YOUR_PIPELINE_ID/current
FRONTEND_TEST_K8S_URL=https://k8s.dev.your-domain.com:40022/...
FRONTEND_TEST_TAG_PATTERN=javaly/jpms-web:(dev-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})

# 后端配置
BACKEND_TEST_YUNXIAO_URL=https://flow.aliyun.com/pipelines/YOUR_PIPELINE_ID/current
BACKEND_TEST_K8S_URL=https://k8s.dev.your-domain.com:40022/...
BACKEND_TEST_TAG_PATTERN=javaly/spms-server:(dev-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})

# K8s 登录凭证
K8S_DEV_USERNAME=your_username
K8S_DEV_PASSWORD=your_password
```

### 3. 启动服务

```bash
# 方式一：使用一键启动脚本（推荐）
./start.sh

# 方式二：分别启动
# 终端 1 - 启动后端
cd server
python3 web_server.py

# 终端 2 - 启动前端
cd web
npm start
```

访问 http://localhost:3000

### 4. 使用界面

界面提供两个项目卡片，每个项目有三个按钮：

**spms-web (前端)**
- **🚀 云效执行** - 仅触发前端云效构建
- **☸️ K8s发布** - 使用最近构建版本更新前端测试环境
- **⚡ 全部** - 完整流程：触发构建 + 更新前端测试环境

**spms-server (后端)**
- **🚀 云效执行** - 仅触发后端云效构建
- **☸️ K8s发布** - 使用最近构建版本更新后端测试环境
- **⚡ 全部** - 完整流程：触发构建 + 更新后端测试环境

首次运行需要手动登录云效和 K8s 控制台，登录后会自动保存状态。

## 📂 项目结构

```
yx2k8s/
├── server/                   # 后端服务
│   ├── web_server.py        # Flask + SocketIO 服务器
│   ├── config.py            # 配置管理
│   ├── yunxiao.py           # 云效操作模块
│   ├── k8s.py               # K8s 操作模块
│   ├── task_scheduler.py    # 任务调度器
│   └── utils.py             # 工具函数
├── web/                      # 前端应用
│   ├── public/              # 静态资源
│   ├── src/
│   │   ├── components/      # React 组件
│   │   │   ├── TaskCard.tsx
│   │   │   ├── LogViewer.tsx
│   │   │   └── Notification.tsx
│   │   ├── App.tsx          # 主应用组件
│   │   └── index.tsx        # 入口文件
│   └── package.json         # 前端依赖
├── start.sh                  # 一键启动脚本
├── requirements.txt          # Python 依赖
├── .env                      # 环境变量配置
├── .env.example              # 环境变量模板
├── auth.json                 # 登录状态存储（自动生成）
└── screenshots/              # 失败时的截图
```

## 🎯 工作流程

### 云效执行模式
```
spms-web: 触发前端构建 → 获取版本号
spms-server: 触发后端构建 → 获取版本号
```

### K8s发布模式
```
spms-web: 获取最近构建版本号 → 更新前端测试环境
spms-server: 获取最近构建版本号 → 更新后端测试环境
```

### 全部模式
```
spms-web: 触发前端构建 → 获取版本号 → 更新前端测试环境
spms-server: 触发后端构建 → 获取版本号 → 更新后端测试环境
```

## ❓ 常见问题

### 1. 首次运行需要登录吗？

是的，首次运行需要手动登录云效和 K8s 控制台。登录后，脚本会自动保存登录状态到 `auth.json`，后续运行无需再次登录。

### 2. 如何切换账号？

删除 `auth.json` 文件，再次运行脚本即可手动登录新账号。

```bash
rm auth.json
python web_server.py
```

### 3. 构建超时怎么办？

默认构建超时时间是 5 分钟，如果构建时间较长，可以在 `config.py` 中调整：

```python
BUILD_TIMEOUT = 600000  # 改为 10 分钟
```

### 4. 失败时如何排查？

脚本失败时会自动截图保存到 `screenshots/` 目录，文件名包含时间戳和错误类型。

### 5. 如何后台运行？

在 `config.py` 中设置：

```python
HEADLESS = True  # 开启无头模式
```

## 🔐 安全说明

- 全程本地执行，不上传任何数据
- 不保存账号密码，仅复用浏览器 Cookie
- 不调用云效 API 和 K8s API，仅模拟浏览器操作
- `auth.json` 文件包含登录凭证，请妥善保管
- `.env` 文件包含敏感 URL，已添加到 `.gitignore`

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

## ⚠️ 免责声明

- 本工具仅用于自动化日常运维操作，请勿用于非法用途
- 使用本工具产生的任何后果由使用者自行承担
- 建议在非生产环境充分测试后再用于生产环境
- 请遵守所在企业的安全规范和操作流程

---

Made with ❤️ by CC
