"""
云效操作模块: 触发构建并获取镜像版本号
"""
import re
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
import config
from utils import log, take_screenshot


async def trigger_build_and_fetch_tag(page: Page, skip_trigger: bool = False) -> str:
    """前端专用: 触发构建并获取 tag"""
    return await _trigger_build_and_fetch_tag(page, skip_trigger=skip_trigger)


async def trigger_backend_build_and_fetch_tag(
    page: Page,
    skip_trigger: bool = False,
    log_job_keyword: str | None = None,
) -> str:
    """
    后端专用: 触发构建并获取 tag

    Args:
        page: Playwright Page 对象
        skip_trigger: 是否跳过触发构建
        log_job_keyword: 日志任务关键词，用于定位特定任务的日志按钮（如 "Java生产环境构建"）
    """
    return await _trigger_build_and_fetch_tag(page, skip_trigger=skip_trigger, log_job_keyword=log_job_keyword)


async def _trigger_build_and_fetch_tag(
    page: Page,
    skip_trigger: bool = False,
    log_job_keyword: str | None = None,
) -> str:
    """
    触发云效构建并获取镜像版本号

    逻辑:
    1. 触发构建(或跳过)
    2. 等待运行成功
    3. 根据 log_job_keyword 定位日志按钮（如果提供），否则使用第一个
    4. 点击日志，展开详细日志，提取 tag
    5. tag 格式: {IMAGE_REGISTRY}/{IMAGE_NAMESPACE}/项目名:分支-时间戳

    Args:
        page: Playwright Page 对象
        skip_trigger: 是否跳过触发构建,仅获取最近一次构建的版本号 (默认 False)
        log_job_keyword: 日志任务关键词，用于定位特定任务的日志按钮（如 "Java生产环境构建"）

    Returns:
        镜像版本号 (例: dev-2025-11-13-17-53-56)

    Raises:
        Exception: 操作失败时抛出异常
    """
    try:
        # 1. 访问 Pipeline 页面
        log("访问云效 Pipeline 页面...", "PROGRESS")
        await page.goto(config.YUNXIAO_URL, timeout=config.PAGE_LOAD_TIMEOUT)
        await page.wait_for_load_state('networkidle')

        # 检查是否需要登录
        # 如果页面上有"登录"相关文字,说明需要手动登录
        login_elements = await page.locator('text=登录').count()
        if login_elements > 0:
            log("⚠️  检测到需要登录,请在浏览器中手动登录后按回车继续...", "WARNING")
            input("按回车继续...")
            await page.wait_for_load_state('networkidle')

        # 关闭可能的引导弹窗
        try:
            # 尝试关闭各种可能的弹窗
            close_buttons = await page.locator('button:has-text("知道了"), button:has-text("关闭"), button:has-text("我知道了"), .next-dialog-close, [aria-label="Close"]').count()
            if close_buttons > 0:
                log("检测到引导弹窗,正在关闭...", "INFO")
                await page.locator('button:has-text("知道了"), button:has-text("关闭"), button:has-text("我知道了"), .next-dialog-close, [aria-label="Close"]').first.click(timeout=3000)
                await page.wait_for_timeout(1000)
        except:
            pass  # 如果没有弹窗或关闭失败,继续执行

        # 2. 检测云效运行状态并决定是否触发新构建
        should_trigger = not skip_trigger
        already_running = False

        if should_trigger:
            log("检查云效运行状态...", "INFO")
            try:
                # 检测"运行中"状态
                running_indicator = page.locator('text=运行中').first
                if await running_indicator.count() > 0 and await running_indicator.is_visible():
                    log("⚠️ 检测到云效已在运行中,跳过触发新构建", "WARNING")
                    log("将等待当前运行中的构建完成", "INFO")
                    already_running = True
                    should_trigger = False
            except Exception as e:
                log(f"检测运行状态时出错(继续执行): {str(e)}", "WARNING")

        # 3. 如果需要触发构建，则点击运行按钮
        if should_trigger:
            log("点击【运行】按钮...", "PROGRESS")
            run_button = page.locator('button:has-text("运行")').first

            # 检查按钮是否可用
            is_disabled = await run_button.is_disabled()
            if is_disabled:
                log("⚠️ 运行按钮被禁用,可能已有构建在运行中", "WARNING")
                log("将等待当前运行中的构建完成", "INFO")
                already_running = True
            else:
                await run_button.click(timeout=config.OPERATION_TIMEOUT)

                # 4. 等待"运行配置"弹窗出现
                await page.wait_for_selector('text=运行配置', state='visible', timeout=config.OPERATION_TIMEOUT)

                # 5. 在弹窗中点击【运行】按钮(确认)
                log("确认运行配置...", "PROGRESS")
                confirm_button = page.locator('.next-dialog >> button:has-text("运行")')
                await confirm_button.click(timeout=config.OPERATION_TIMEOUT)

                # 6. 等待弹窗关闭
                await page.wait_for_selector('text=运行配置', state='hidden', timeout=config.OPERATION_TIMEOUT)
                log("✓ 已触发新的构建", "SUCCESS")
        elif skip_trigger and not already_running:
            log("⏭️  跳过触发构建,将从最近一次构建中获取版本号", "INFO")

        # 6. 等待构建完成
        log("等待构建完成(最长5分钟)...", "WAITING")
        try:
            # 策略1: 等待"运行成功"标志出现
            await page.wait_for_selector('text=运行成功', timeout=config.BUILD_TIMEOUT)

            # 策略2: 循环检查,确保没有loading状态
            # log("等待所有阶段完成...", "WAITING")
            # max_wait_seconds = 60
            # for i in range(max_wait_seconds):
            #     # 检查页面上是否还有 loading/spinning 类的元素
            #     loading_count = await page.locator('[class*="loading"], [class*="spinning"], [class*="running"]').count()

            #     if loading_count == 0:
            #         log(f"所有阶段已完成(等待了{i+1}秒)", "SUCCESS")
            #         break

            #     # 每秒检查一次
            #     await page.wait_for_timeout(1000)

            #     if i % 5 == 0 and i > 0:
            #         log(f"仍在等待阶段完成... ({i}秒)", "INFO")
            # else:
            #     # 超过60秒仍未完成,继续执行(可能只是动画未消失)
            #     log("等待超时,但继续尝试获取日志", "WARNING")

            log("构建已完成", "SUCCESS")

        except PlaywrightTimeoutError:
            log("等待构建超时,可能构建失败或时间过长", "ERROR")
            await take_screenshot(page, "build_timeout")
            raise Exception("构建超时")

        # 7. 定位日志按钮
        log("查找日志按钮...", "PROGRESS")
        log_button = None

        # 如果提供了任务关键词，则定位包含该关键词的任务卡片中的日志按钮
        if log_job_keyword:
            log(f"根据关键词定位日志按钮: {log_job_keyword}", "INFO")
            try:
                # 定位包含关键词的任务卡片
                # DOM: <div class="flow-job-new--hoverableWrapper--p4fKlSv"> 包含任务名称和日志按钮
                job_card = page.locator('div.flow-job-new--hoverableWrapper--p4fKlSv').filter(has_text=log_job_keyword).first
                if await job_card.count() > 0:
                    # 在该任务卡片中查找日志按钮
                    btn = job_card.locator('button:has-text("日志")').first
                    if await btn.count() > 0:
                        log_button = btn
                        log(f"✓ 找到包含 '{log_job_keyword}' 的日志按钮", "SUCCESS")
            except Exception as e:
                log(f"通过关键词定位失败: {str(e)}", "WARNING")

        # 如果没有提供关键词或定位失败，使用第一个日志按钮
        if not log_button:
            log_buttons = page.locator('button:has-text("日志")')
            button_count = await log_buttons.count()
            if button_count == 0:
                log("未找到任何日志按钮", "ERROR")
                await take_screenshot(page, "no_log_buttons")
                raise Exception("未找到日志按钮")
            log_button = log_buttons.first
            log(f"使用第一个日志按钮 (共找到 {button_count} 个)", "INFO")

        # 8. 点击日志按钮
        await log_button.click(timeout=5000)
        await page.wait_for_timeout(2000)

        # 9. 尝试展开详细日志
        try:
            log_elements = page.get_by_text(config.YUNXIAO_LOG_EXPAND_TEXT, exact=False)
            if await log_elements.count() > 0:
                await log_elements.first.click(timeout=5000)
                await page.wait_for_timeout(2000)
                log("已展开镜像构建日志", "INFO")
        except Exception as e:
            log(f"展开详细日志失败(继续尝试): {str(e)}", "WARNING")

        # 10. 从日志弹窗获取 tag
        log("尝试提取版本号...", "PROGRESS")
        tag = None

        # 定义统一的 tag 正则（固定格式）
        # 格式: {IMAGE_REGISTRY}/{IMAGE_NAMESPACE}/项目名:分支-时间戳
        # tag 部分匹配: 字母数字和连字符,遇到逗号、分号、空格、引号等停止
        registry_escaped = config.IMAGE_REGISTRY.replace('.', r'\.')
        unified_tag_pattern = rf'{registry_escaped}/{config.IMAGE_NAMESPACE}/[^:]+:([a-zA-Z0-9\-]+)'

        try:
            await page.wait_for_selector('.log-container__body .log-panel__context.right', state='visible', timeout=10000)
            log_container = page.locator('.log-container__body .log-panel__context.right').first

            # 滚动到日志底部
            log("滚动日志到底部...", "INFO")
            await log_container.evaluate('el => { el.scrollTop = el.scrollHeight }')
            await page.wait_for_timeout(600)
            await log_container.evaluate('el => { el.scrollTop = el.scrollHeight }')
            await page.wait_for_timeout(300)

            # 获取日志文本
            log_text = await log_container.inner_text()

            # 使用统一的 tag 正则提取
            match = re.search(unified_tag_pattern, log_text)
            if match:
                tag = match.group(1)
                log(f"✓ 从日志获取到版本号: {tag}", "SUCCESS")
            else:
                log("日志中未找到 tag", "WARNING")

        except Exception as e:
            log(f"从日志获取 tag 失败: {str(e)}", "WARNING")

        # 11. 关闭日志弹窗
        try:
            close_button = page.locator('.next-dialog >> button.next-dialog-close')
            await close_button.click(timeout=3000)
            await page.wait_for_timeout(500)
        except:
            pass

        # 12. 验证结果
        if not tag:
            log("未能获取到版本号", "ERROR")
            await take_screenshot(page, "tag_not_found")
            raise Exception("无法获取镜像版本号")

        return tag

    except PlaywrightTimeoutError as e:
        log(f"操作超时: {str(e)}", "ERROR")
        await take_screenshot(page, "yunxiao_timeout")
        raise Exception(f"云效操作超时: {str(e)}")

    except Exception as e:
        log(f"云效操作失败: {str(e)}", "ERROR")
        await take_screenshot(page, "yunxiao_error")
        raise
