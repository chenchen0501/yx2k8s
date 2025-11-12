"""
云效操作模块: 触发构建并获取镜像版本号
"""
import re
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
import config
from utils import log, take_screenshot


async def trigger_build_and_fetch_tag(page: Page) -> str:
    """
    触发云效构建并获取镜像版本号

    Args:
        page: Playwright Page 对象

    Returns:
        镜像版本号 (例: dev-2025-11-12-14-20-32)

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

        # # 2. 点击【运行】按钮
        log("点击【运行】按钮...", "PROGRESS")
        run_button = page.locator('button:has-text("运行")').first
        await run_button.click(timeout=config.OPERATION_TIMEOUT)

        # 3. 等待"运行配置"弹窗出现
        await page.wait_for_selector('text=运行配置', state='visible', timeout=config.OPERATION_TIMEOUT)

        # 4. 在弹窗中点击【运行】按钮(确认)
        log("确认运行配置...", "PROGRESS")
        confirm_button = page.locator('.next-dialog >> button:has-text("运行")')
        await confirm_button.click(timeout=config.OPERATION_TIMEOUT)

        # 5. 等待弹窗关闭
        await page.wait_for_selector('text=运行配置', state='hidden', timeout=config.OPERATION_TIMEOUT)

        # 6. 等待构建完成
        log("等待构建完成(最长5分钟)...", "WAITING")
        try:
            # 策略1: 等待"运行成功"标志出现
            await page.wait_for_selector('text=运行成功', timeout=config.BUILD_TIMEOUT)

            # 策略2: 循环检查,确保没有loading状态
            log("等待所有阶段完成...", "WAITING")
            max_wait_seconds = 60
            for i in range(max_wait_seconds):
                # 检查页面上是否还有 loading/spinning 类的元素
                loading_count = await page.locator('[class*="loading"], [class*="spinning"], [class*="running"]').count()

                if loading_count == 0:
                    log(f"所有阶段已完成(等待了{i+1}秒)", "SUCCESS")
                    break

                # 每秒检查一次
                await page.wait_for_timeout(1000)

                if i % 5 == 0 and i > 0:
                    log(f"仍在等待阶段完成... ({i}秒)", "INFO")
            else:
                # 超过60秒仍未完成,继续执行(可能只是动画未消失)
                log("等待超时,但继续尝试获取日志", "WARNING")

            log("构建已完成", "SUCCESS")

        except PlaywrightTimeoutError:
            log("等待构建超时,可能构建失败或时间过长", "ERROR")
            await take_screenshot(page, "build_timeout")
            raise Exception("构建超时")

        # 7. 展开构建日志
        log("查找并展开构建日志...", "PROGRESS")

        await page.locator('text=日志').first.click(timeout=5000)
        await page.wait_for_timeout(2000)

        # 策略: 依次尝试多种方式打开日志
        log_opened = False

        # 方式1: 尝试点击页面上任何包含"镜像构建"的可点击元素
        try:
            # 查找所有包含"镜像构建并推送"的元素
            log_elements = page.get_by_text("镜像构建并推送", exact=False)
            count = await log_elements.count()
            log(f"找到 {count} 个包含'镜像构建并推送'的元素", "INFO")

            if count > 0:
                # 尝试点击第一个
                await log_elements.first.click(timeout=5000)
                await page.wait_for_timeout(2000)
                log_opened = True
                log("成功点击日志项", "SUCCESS")
        except Exception as e:
            log(f"方式1失败: {str(e)}", "WARNING")

       
        # 8. 尝试获取版本号 - 多种方式
        log("尝试提取版本号...", "PROGRESS")
        tag = None

        # 方式A: 如果日志已打开,从日志弹窗获取
        if log_opened:
            try:
                # 右侧日志正文容器：class="log-panel__context right" 位于 .log-container__body 下
                await page.wait_for_selector('.log-container__body .log-panel__context.right', state='visible', timeout=10000)
                log_container = page.locator('.log-container__body .log-panel__context.right').first

                # 滚动到日志底部(版本号通常在最后)
                log("滚动日志到底部...", "INFO")
                # 方式1：直接设置 scrollTop
                await log_container.evaluate('el => { el.scrollTop = el.scrollHeight }')
                await page.wait_for_timeout(600)  # 等待滚动完成

                # 再次滚动确保到底
                await log_container.evaluate('el => { el.scrollTop = el.scrollHeight }')
                await page.wait_for_timeout(300)

                # 方式2（兜底）：将最后一行滚动到可视区域
                try:
                    last_line = page.locator('.log-container__body .log-panel__context.right > div').last
                    await last_line.scroll_into_view_if_needed(timeout=2000)
                    await page.wait_for_timeout(300)
                except:
                    pass

                # 获取日志文本
                log_text = await log_container.inner_text()

                match = re.search(config.TAG_PATTERN, log_text)
                if match:
                    tag = match.group(1)
                    log(f"从日志弹窗获取到版本号: {tag}", "SUCCESS")
            except Exception as e:
                log(f"从日志弹窗获取版本号失败: {str(e)}", "WARNING")

        # 如果所有方式都失败
        if not tag:
            log("所有方式都未能获取版本号,保存截图...", "ERROR")
            await take_screenshot(page, "tag_not_found")
            raise Exception("无法获取镜像版本号")

        # 9. 关闭可能打开的日志弹窗
        if log_opened:
            try:
                close_button = page.locator('.next-dialog >> button.next-dialog-close')
                await close_button.click(timeout=3000)
                log("已关闭日志弹窗", "INFO")
            except:
                pass  # 如果关闭失败,忽略

        return tag

    except PlaywrightTimeoutError as e:
        log(f"操作超时: {str(e)}", "ERROR")
        await take_screenshot(page, "yunxiao_timeout")
        raise Exception(f"云效操作超时: {str(e)}")

    except Exception as e:
        log(f"云效操作失败: {str(e)}", "ERROR")
        await take_screenshot(page, "yunxiao_error")
        raise
