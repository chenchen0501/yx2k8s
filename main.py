#!/usr/bin/env python3
"""
云效到 K8s 镜像版本自动更新工具

功能:
1. 触发云效构建并获取最新镜像版本号
2. 自动更新 K8s Deployment 镜像版本

使用方法:
    python main.py

首次运行需要手动登录云效和 K8s 控制台,登录信息会自动保存。
"""
import os
import sys
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

import config
from utils import log, take_screenshot, format_duration
from yunxiao import trigger_build_and_fetch_tag
from k8s import update_deployment_image


async def main():
    """主流程"""
    start_time = datetime.now()

    log("=" * 60, "INFO")
    log("云效到 K8s 镜像版本自动更新工具", "INFO")
    log("=" * 60, "INFO")

    async with async_playwright() as p:
        # 启动浏览器
        log(f"启动浏览器 (无头模式: {config.HEADLESS})...", "INFO")

        browser = await p.chromium.launch(
            headless=config.HEADLESS,
            # 后台运行
            # args=['--headless=new'],
            
            # 设置浏览器参数
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
            ]
        )

        # 创建浏览器上下文
        # 如果存在 auth.json,则复用登录状态
        context_options = {}

        if os.path.exists(config.AUTH_FILE):
            log(f"检测到登录状态文件: {config.AUTH_FILE}", "INFO")
            context_options['storage_state'] = config.AUTH_FILE
        else:
            log("首次运行,需要手动登录云效和 K8s 控制台", "WARNING")

        context = await browser.new_context(**context_options)

        # 设置默认超时
        context.set_default_timeout(config.OPERATION_TIMEOUT)

        # 创建页面
        page = await context.new_page()

        try:
            # ==================== Step 1: 云效获取版本号 ====================
            log("\n【步骤 1/2】云效: 触发构建并获取镜像版本号", "INFO")
            log("-" * 60, "INFO")

            tag = await trigger_build_and_fetch_tag(page)

            # 立即保存登录状态(云效部分完成后)
            await context.storage_state(path=config.AUTH_FILE)
            log(f"云效登录状态已保存到: {config.AUTH_FILE}", "INFO")

            log("-" * 60, "INFO")
            log(f"【步骤 1/2】完成! 版本号: {tag}", "SUCCESS")

            # ==================== Step 2: K8s 更新镜像版本 ====================
            log("\n【步骤 2/2】K8s: 更新 Deployment 镜像版本", "INFO")
            log("-" * 60, "INFO")

            await update_deployment_image(page, tag)

            log("-" * 60, "INFO")
            log("【步骤 2/2】完成!", "SUCCESS")

            # 再次保存登录状态(包含 K8s 登录信息)
            await context.storage_state(path=config.AUTH_FILE)
            log(f"登录状态已更新到: {config.AUTH_FILE}", "INFO")

            # 计算总耗时
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            log("\n" + "=" * 60, "INFO")
            log(f"🎉 任务全部完成! 耗时: {format_duration(duration)}", "SUCCESS")
            log("=" * 60, "INFO")

            # 等待 3 秒后关闭浏览器
            if not config.HEADLESS:
                log("浏览器将在 3 秒后关闭...", "INFO")
                await page.wait_for_timeout(3000)

        except KeyboardInterrupt:
            log("\n用户中断操作", "WARNING")

            # 尝试保存登录状态
            try:
                await context.storage_state(path=config.AUTH_FILE)
                log(f"登录状态已保存", "INFO")
            except:
                pass

            sys.exit(1)

        except Exception as e:
            log(f"\n任务失败: {str(e)}", "ERROR")

            # 尝试保存登录状态(即使失败也保存)
            try:
                await context.storage_state(path=config.AUTH_FILE)
                log(f"登录状态已保存(失败时)", "INFO")
            except:
                log("无法保存登录状态", "WARNING")

            # 截图
            if config.SCREENSHOT_ON_ERROR:
                await take_screenshot(page, "final_error")

            # 计算耗时
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            log(f"失败前运行时长: {format_duration(duration)}", "INFO")

            sys.exit(1)

        finally:
            # 关闭浏览器
            await browser.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序已终止")
        sys.exit(0)
