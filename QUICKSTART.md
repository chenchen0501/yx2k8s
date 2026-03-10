# 快速使用指南

## 1. 安装依赖

```bash
pip install -r requirements.txt
playwright install chromium
cd web && npm install && cd ..
```

## 2. 配置环境变量

编辑 `.env` 文件，填入你的云效和 K8s 地址。

## 3. 启动服务

```bash
./start.sh
```

## 4. 访问界面

打开浏览器访问: http://localhost:3000

## 5. 使用按钮

每个项目（spms-web、spms-server）有三个按钮：

- **🚀 云效执行**: 仅触发云效构建
- **☸️ K8s发布**: 使用最近构建版本更新 K8s 测试环境
- **⚡ 全部**: 完整流程（构建+发布）

首次使用需要手动登录云效和 K8s 控制台。
