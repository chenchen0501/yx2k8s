#!/usr/bin/env python3
"""
任务调度器 - 支持多任务并行/串行执行
"""
import asyncio
from typing import List, Dict, Callable, Any
from datetime import datetime
from playwright.async_api import async_playwright
import config
from utils import log
from yunxiao import trigger_build_and_fetch_tag, trigger_backend_build_and_fetch_tag
from k8s import update_deployment_image


class DeployTask:
    """部署任务定义"""

    def __init__(self, task_id: str, name: str, project: str, env: str, run_build: bool = True):
        """
        Args:
            task_id: 任务ID (如 'frontend-test')
            name: 任务名称 (如 '前端测试环境')
            project: 项目类型 ('frontend' 或 'backend')
            env: 环境类型 ('test' 或 'prod')
            run_build: 是否触发云效构建 (默认 True)
                       - True: 触发新构建并获取版本号
                       - False: 跳过触发,从最近一次构建中获取版本号
        """
        self.task_id = task_id
        self.name = name
        self.project = project
        self.env = env
        self.run_build = run_build
        self.status = 'pending'  # pending, running, success, error
        self.error_message = None
        self.start_time = None
        self.end_time = None
        self.tag = None  # 镜像版本号

    def get_config(self) -> Dict[str, str]:
        """获取任务对应的配置"""
        if self.project == 'frontend':
            return config.FRONTEND_CONFIG[self.env]
        elif self.project == 'backend':
            return config.BACKEND_CONFIG[self.env]
        else:
            raise ValueError(f"未知的项目类型: {self.project}")


class TaskScheduler:
    """任务调度器"""

    def __init__(self, log_callback: Callable[[str, str], None] = None):
        """
        Args:
            log_callback: 日志回调函数 (message, level)
        """
        self.log_callback = log_callback or log
        self.tasks: List[DeployTask] = []
        self.browser = None
        self.context = None
        self.page = None
        self.tag_cache: Dict[str, str] = {}

    def add_task(self, task: DeployTask):
        """添加任务"""
        self.tasks.append(task)
        self._log(f"添加任务: {task.name}", "INFO")

    def _log(self, message: str, level: str = "INFO"):
        """统一日志输出"""
        self.log_callback(message, level)

    async def execute_all(self):
        """执行所有任务"""
        if not self.tasks:
            self._log("没有任务需要执行", "WARNING")
            return

        self._log(f"共有 {len(self.tasks)} 个任务待执行", "INFO")
        self._log("-" * 60, "INFO")

        # 初始化浏览器
        await self._init_browser()

        try:
            # 按顺序执行每个任务
            for i, task in enumerate(self.tasks, 1):
                self._log(f"\n【任务 {i}/{len(self.tasks)}】{task.name}", "INFO")
                self._log("=" * 60, "INFO")

                await self._execute_task(task)

                # 保存登录状态
                await self.context.storage_state(path=config.AUTH_FILE)

                if task.status == 'success':
                    self._log(f"✅ 【任务 {i}/{len(self.tasks)}】{task.name} 完成!", "SUCCESS")
                else:
                    self._log(f"❌ 【任务 {i}/{len(self.tasks)}】{task.name} 失败: {task.error_message}", "ERROR")

                self._log("=" * 60, "INFO")

            # 输出总结
            self._print_summary()

        finally:
            await self._cleanup()

    async def _init_browser(self):
        """初始化浏览器"""
        import os

        self._log(f"启动浏览器 (无头模式: {config.HEADLESS})...", "INFO")

        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=config.HEADLESS,
            args=['--headless=new'] if config.HEADLESS else []
        )

        # 创建浏览器上下文
        context_options = {}
        if os.path.exists(config.AUTH_FILE):
            self._log(f"检测到登录状态文件: {config.AUTH_FILE}", "INFO")
            context_options['storage_state'] = config.AUTH_FILE
        else:
            self._log("首次运行,需要手动登录云效和 K8s 控制台", "WARNING")

        self.context = await self.browser.new_context(**context_options)
        self.context.set_default_timeout(config.OPERATION_TIMEOUT)

        # 创建页面
        self.page = await self.context.new_page()

    async def _execute_task(self, task: DeployTask):
        """执行单个任务"""
        task.status = 'running'
        task.start_time = datetime.now()

        try:
            # 获取任务配置
            task_config = task.get_config()
            yunxiao_url = task_config['yunxiao_url']
            k8s_url = task_config['k8s_url']
            tag_pattern = task_config['tag_pattern']

            # 验证配置
            if not k8s_url:
                raise Exception(f"K8s URL 配置不完整: k8s_url={k8s_url}")

            if task.run_build and not yunxiao_url:
                raise Exception(f"云效 URL 配置不完整: yunxiao_url={yunxiao_url}")

            # 临时替换 config 中的全局变量(兼容现有代码)
            original_yunxiao_url = config.YUNXIAO_URL
            original_k8s_url = config.K8S_URL
            original_tag_pattern = config.TAG_PATTERN
            original_k8s_username = getattr(config, "K8S_USERNAME", "")
            original_k8s_password = getattr(config, "K8S_PASSWORD", "")

            config.YUNXIAO_URL = yunxiao_url
            config.K8S_URL = k8s_url
            config.TAG_PATTERN = tag_pattern
            config.K8S_USERNAME = task_config.get('k8s_username', '')
            config.K8S_PASSWORD = task_config.get('k8s_password', '')

            try:
                # Step 1: 云效获取版本号 (始终执行,但可能跳过触发新构建)
                cache_key = task.project
                cached_tag = self.tag_cache.get(cache_key)
                tag = None

                # 根据项目类型选择触发函数和参数
                if task.project == 'backend':
                    # 后端：从配置中获取日志任务关键词
                    log_job_keyword = task_config.get('log_job_keyword')
                    if log_job_keyword:
                        self._log(f"日志任务关键词: {log_job_keyword}", "INFO")
                else:
                    log_job_keyword = None

                if task.run_build:
                    if cached_tag:
                        self._log(f"步骤 1/2: 复用本次会话已构建的 {task.project} 版本号", "INFO")
                        self._log(f"版本号: {cached_tag}", "INFO")
                        tag = cached_tag
                    else:
                        self._log(f"步骤 1/2: 触发云效构建并获取镜像版本号", "INFO")
                        self._log(f"云效地址: {yunxiao_url}", "INFO")
                        if task.project == 'backend':
                            tag = await trigger_backend_build_and_fetch_tag(
                                self.page, skip_trigger=False, log_job_keyword=log_job_keyword
                            )
                        else:
                            tag = await trigger_build_and_fetch_tag(self.page, skip_trigger=False)
                        self.tag_cache[cache_key] = tag
                        self._log(f"✅ 获取到版本号: {tag}", "SUCCESS")
                else:
                    if cached_tag:
                        self._log(f"步骤 1/2: 复用本次会话缓存的 {task.project} 版本号", "INFO")
                        self._log(f"版本号: {cached_tag}", "INFO")
                        tag = cached_tag
                    else:
                        self._log(f"步骤 1/2: 从最近一次云效构建中获取镜像版本号 (跳过触发)", "INFO")
                        self._log(f"云效地址: {yunxiao_url}", "INFO")
                        if task.project == 'backend':
                            tag = await trigger_backend_build_and_fetch_tag(
                                self.page, skip_trigger=True, log_job_keyword=log_job_keyword
                            )
                        else:
                            tag = await trigger_build_and_fetch_tag(self.page, skip_trigger=True)
                        self.tag_cache[cache_key] = tag
                        self._log(f"✅ 获取到版本号: {tag}", "SUCCESS")

                task.tag = tag

                # Step 2: K8s 更新镜像版本
                self._log(f"\n步骤 2/2: 更新 K8s Deployment 镜像版本", "INFO")
                self._log(f"K8s 地址: {k8s_url}", "INFO")
                await update_deployment_image(self.page, tag)
                self._log(f"✅ 镜像版本更新成功!", "SUCCESS")

                task.status = 'success'

            finally:
                # 恢复原始配置
                config.YUNXIAO_URL = original_yunxiao_url
                config.K8S_URL = original_k8s_url
                config.TAG_PATTERN = original_tag_pattern
                config.K8S_USERNAME = original_k8s_username
                config.K8S_PASSWORD = original_k8s_password

        except Exception as e:
            task.status = 'error'
            task.error_message = str(e)
            self._log(f"任务执行失败: {str(e)}", "ERROR")

        finally:
            task.end_time = datetime.now()

    async def _cleanup(self):
        """清理资源"""
        if self.page:
            # 等待一下再关闭
            if not config.HEADLESS:
                self._log("浏览器将在 3 秒后关闭...", "INFO")
                await self.page.wait_for_timeout(3000)

        if self.browser:
            await self.browser.close()

    def _print_summary(self):
        """打印执行总结"""
        self._log("\n" + "=" * 60, "INFO")
        self._log("📊 执行总结", "INFO")
        self._log("=" * 60, "INFO")

        success_count = sum(1 for t in self.tasks if t.status == 'success')
        error_count = sum(1 for t in self.tasks if t.status == 'error')

        for i, task in enumerate(self.tasks, 1):
            status_icon = "✅" if task.status == 'success' else "❌"
            duration = (task.end_time - task.start_time).total_seconds() if task.end_time else 0

            self._log(f"{status_icon} {i}. {task.name}: {task.status.upper()} (耗时: {duration:.1f}秒)",
                     "SUCCESS" if task.status == 'success' else "ERROR")

            if task.tag:
                self._log(f"   版本号: {task.tag}", "INFO")

            if task.error_message:
                self._log(f"   错误: {task.error_message}", "ERROR")

        self._log("-" * 60, "INFO")
        self._log(f"总计: {len(self.tasks)} 个任务, 成功 {success_count} 个, 失败 {error_count} 个",
                 "SUCCESS" if error_count == 0 else "WARNING")
        self._log("=" * 60, "INFO")
