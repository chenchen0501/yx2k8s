# 使用说明

## 新功能说明

项目已扩展支持前端后端的云效打包和 K8s 发版,包括生产和测试环境。

### 支持的环境

1. **前端测试环境** (Frontend Test)
2. **前端生产环境** (Frontend Prod)
3. **后端测试环境** (Backend Test)
4. **后端生产环境** (Backend Prod)

### Web 界面功能

访问 http://localhost:5001 后,你会看到:

#### 1. 云效运行全局开关 🚀

- **[ ] 云效运行 (全局)**
  - ✅ 勾选: 触发云效构建 + 更新 K8s (完整部署流程)
  - ⏭️ 取消: 仅更新 K8s 版本 (需要手动输入版本号)

**默认勾选**。取消勾选后,点击部署时会提示输入镜像版本号。

#### 2. 任务选择区域

- **前端 (Frontend)**

  - [ ] 测试环境 (Test)
  - [ ] 生产环境 (Prod)

- **后端 (Backend)**
  - [ ] 测试环境 (Test)
  - [ ] 生产环境 (Prod)

默认全部勾选,可以根据需要取消勾选。

#### 3. 快捷操作按钮

- **全选**: 选中所有 4 个环境
- **取消全选**: 取消所有选择
- **仅前端**: 只选择前端测试和生产
- **仅后端**: 只选择后端测试和生产

#### 4. 开始部署按钮

点击后会:

1. 检查是否需要云效构建
   - 如果取消了【云效运行】,会弹出输入框要求输入版本号
2. 显示确认弹窗,列出部署模式和任务列表
3. 确认后开始执行
4. 实时显示每个任务的执行日志
5. 任务按顺序依次执行

## 配置环境变量

在 `.env` 文件中配置所有环境:

```bash
# ==================== 前端配置 ====================
# 前端测试环境
FRONTEND_TEST_YUNXIAO_URL=https://flow.aliyun.com/pipelines/YOUR_FRONTEND_TEST_PIPELINE/current
FRONTEND_TEST_K8S_URL=https://k8s.dev.example.com/.../Deployment/jpms-web
FRONTEND_TEST_TAG_PATTERN=javaly/jpms-web:(dev-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})

# 前端生产环境
FRONTEND_PROD_YUNXIAO_URL=https://flow.aliyun.com/pipelines/YOUR_FRONTEND_PROD_PIPELINE/current
FRONTEND_PROD_K8S_URL=https://k8s.prod.example.com/.../Deployment/jpms-web
FRONTEND_PROD_TAG_PATTERN=javaly/jpms-web:(prod-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})

# ==================== 后端配置 ====================
# 后端测试环境
BACKEND_TEST_YUNXIAO_URL=https://flow.aliyun.com/pipelines/YOUR_BACKEND_TEST_PIPELINE/current
BACKEND_TEST_K8S_URL=https://k8s.dev.example.com/.../Deployment/jpms-server
BACKEND_TEST_TAG_PATTERN=javaly/jpms-server:(dev-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})

# 后端生产环境
BACKEND_PROD_YUNXIAO_URL=https://flow.aliyun.com/pipelines/YOUR_BACKEND_PROD_PIPELINE/current
BACKEND_PROD_K8S_URL=https://k8s.prod.example.com/.../Deployment/jpms-server
BACKEND_PROD_TAG_PATTERN=javaly/jpms-server:(prod-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})

# ==================== K8s 登录凭证（按环境） ====================
K8S_DEV_USERNAME=your-dev-username
K8S_DEV_PASSWORD=your-dev-password
K8S_PROD_USERNAME=your-prod-username
K8S_PROD_PASSWORD=your-prod-password
```

## 使用流程

### 1. 启动 Web 服务

```bash
python web_server.py
```

看到以下输出表示启动成功:

```
============================================================
云效 K8s 自动部署 Web 服务
============================================================
本地访问: http://localhost:5001
局域网访问: http://<本机IP>:5001
============================================================
```

### 2. 打开浏览器

访问 http://localhost:5001

### 3. 选择部署模式和环境

#### 选择是否运行云效构建

- **勾选【云效运行】**: 完整部署(触发云效构建 + 更新 K8s)
- **取消勾选【云效运行】**: 仅更新 K8s(需手动输入版本号)

#### 选择要部署的环境

根据需要勾选:

- 只部署前端测试? → 只勾选 "前端 > 测试环境"
- 只部署生产? → 点击 "取消全选" 然后勾选两个生产环境
- 全部部署? → 保持默认全选

### 4. 点击【开始部署】

- 如果取消了【云效运行】,会提示输入版本号(例如: dev-2025-11-13-15-20-30)
- 会弹出确认对话框,显示部署模式和任务列表
- 确认后开始执行
- 可以在日志区域实时查看进度

### 5. 查看执行结果

每个任务完成后会显示:

- ✅ 成功标志
- 获取到的镜像版本号
- 总耗时

如果失败:

- ❌ 失败标志
- 错误信息
- 错误截图保存在 `screenshots/` 目录

## 执行日志示例

```
[15:10:23] [INFO] 开始执行部署任务
[15:10:23] [INFO] 共有 2 个任务待执行
[15:10:23] [INFO] 添加任务: 前端测试环境
[15:10:23] [INFO] 添加任务: 前端生产环境

[15:10:25] [INFO] 【任务 1/2】前端测试环境
[15:10:25] [INFO] 步骤 1/2: 触发云效构建并获取镜像版本号
[15:10:45] [SUCCESS] ✅ 获取到版本号: dev-2025-11-13-15-10-43
[15:10:45] [INFO] 步骤 2/2: 更新 K8s Deployment 镜像版本
[15:11:05] [SUCCESS] ✅ 镜像版本更新成功!
[15:11:05] [SUCCESS] ✅ 【任务 1/2】前端测试环境 完成!

[15:11:05] [INFO] 【任务 2/2】前端生产环境
[15:11:05] [INFO] 步骤 1/2: 触发云效构建并获取镜像版本号
[15:11:25] [SUCCESS] ✅ 获取到版本号: prod-2025-11-13-15-11-23
[15:11:25] [INFO] 步骤 2/2: 更新 K8s Deployment 镜像版本
[15:11:45] [SUCCESS] ✅ 镜像版本更新成功!
[15:11:45] [SUCCESS] ✅ 【任务 2/2】前端生产环境 完成!

[15:11:45] [SUCCESS] ✅ 所有任务执行成功! 成功 2 个
```

## 常见使用场景

### 场景 1: 只部署前端测试环境

1. 点击 "取消全选"
2. 勾选 "前端 > 测试环境"
3. 点击 "开始部署"

### 场景 2: 前端测试和生产一起部署

1. 点击 "仅前端"
2. 点击 "开始部署"

### 场景 3: 全部环境一起部署

1. 保持默认全选
2. 点击 "开始部署"

### 场景 4: 只部署生产环境

1. 点击 "取消全选"
2. 勾选 "前端 > 生产环境"
3. 勾选 "后端 > 生产环境"
4. 点击 "开始部署"

## 注意事项

1. **首次运行需要登录**: 程序会检测到需要登录,在浏览器中手动登录后按回车继续
2. **任务按顺序执行**: 多个任务会依次执行,不是并行的
3. **避免重复运行**: 一个任务执行期间,按钮会被禁用,避免重复触发
4. **构建时间较长**: 云效构建通常需要 2-5 分钟,请耐心等待
5. **保持浏览器标签页打开**: 关闭标签页会断开 WebSocket 连接,但不影响后台任务执行

## 技术实现

### 核心模块

1. **task_scheduler.py**: 任务调度器

   - `DeployTask`: 单个部署任务
   - `TaskScheduler`: 管理多个任务的执行

2. **web_server.py**: Web 服务

   - Flask HTTP 接口
   - WebSocket 实时日志推送
   - 任务状态管理

3. **config.py**: 配置管理
   - 从 `.env` 读取 4 种环境配置
   - 超时时间配置
   - 浏览器配置

### 工作流程

```
用户选择任务 → Web 界面
           ↓
   POST /api/deploy (tasks: ['frontend-test', 'backend-prod'])
           ↓
   TaskScheduler 创建任务队列
           ↓
   依次执行每个任务:
     1. 触发云效构建
     2. 等待构建完成
     3. 提取镜像版本号
     4. 更新 K8s Deployment
           ↓
   通过 WebSocket 实时推送日志
           ↓
   返回执行结果
```

## 故障排查

### 问题 1: Web 服务启动失败 - 端口占用

**错误信息**: `Address already in use`

**解决方法**:

```bash
# 杀掉占用端口的进程
lsof -ti:5001 | xargs kill -9

# 或修改端口号(web_server.py 最后几行)
PORT = 5002  # 改为其他端口
```

### 问题 2: 任务执行失败 - 配置错误

**错误信息**: `配置不完整: yunxiao_url=, k8s_url=`

**解决方法**: 检查 `.env` 文件中对应环境的配置是否填写完整

### 问题 3: 版本号提取失败

**错误信息**: `无法获取镜像版本号`

**解决方法**:

1. 检查 `TAG_PATTERN` 正则表达式是否匹配实际的镜像版本格式
2. 设置 `HEADLESS = False` 打开浏览器查看构建日志
3. 查看 `screenshots/` 目录的错误截图

### 问题 4: 登录状态失效

**解决方法**:

```bash
# 删除登录状态文件
rm auth.json

# 重新运行,会提示手动登录
python web_server.py
```

## 更多帮助

如有问题,请查看:

- 项目根目录的 `README.md`
- `screenshots/` 目录的错误截图
- 控制台的详细日志输出
