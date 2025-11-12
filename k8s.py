"""
K8s 操作模块: 更新 Deployment 镜像版本
"""
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
import config
from utils import log, take_screenshot


async def update_deployment_image(page: Page, new_tag: str) -> None:
    """
    更新 K8s Deployment 镜像版本

    Args:
        page: Playwright Page 对象
        new_tag: 新的镜像版本号 (例: dev-2025-11-12-14-20-32)

    Raises:
        Exception: 操作失败时抛出异常
    """
    try:
        # 1. 访问 Deployment 详情页
        log("访问 K8s Deployment 页面...", "PROGRESS")
        await page.goto(config.K8S_URL, timeout=config.PAGE_LOAD_TIMEOUT)
        await page.wait_for_load_state('networkidle')

        # 检查是否需要登录
        login_elements = await page.locator('text=登录').count()
        if login_elements > 0:
            log("⚠️  检测到需要登录 K8s,请在浏览器中手动登录后按回车继续...", "WARNING")
            input("按回车继续...")
            await page.wait_for_load_state('networkidle')

        # 2. 点击【调整镜像版本】按钮
        log("点击【调整镜像版本】按钮...", "PROGRESS")
        adjust_button = page.locator('button:has-text("调整镜像版本")')
        await adjust_button.click(timeout=config.OPERATION_TIMEOUT)

        # 3. 等待弹窗出现
        await page.wait_for_selector('text=调整镜像版本', state='visible', timeout=config.OPERATION_TIMEOUT)
        log("调整镜像版本弹窗已打开", "INFO")

        # 4. 定位"新版本"输入框
        log(f"填入新版本号: {new_tag}", "PROGRESS")

        # 尝试多种方式定位输入框
        input_field = None

        # 方式1: 通过表格最后一列定位
        try:
            input_selector = 'table >> tbody >> tr >> td:last-child >> input'
            input_field = page.locator(input_selector).first
            await input_field.wait_for(state='visible', timeout=5000)
            log("通过表格定位到输入框", "INFO")
        except:
            pass

        # 方式2: 通过 input 类名定位
        if not input_field:
            try:
                input_field = page.locator('input[class*="input__inner"]').first
                await input_field.wait_for(state='visible', timeout=5000)
                log("通过类名定位到输入框", "INFO")
            except:
                pass

        if not input_field:
            raise Exception("无法定位到输入框")

        # 5. 清空并填入新版本
        log(f"准备填入版本号: {new_tag}", "INFO")

        # 先点击聚焦(点击3次确保聚焦)
        await input_field.click(click_count=3)
        await page.wait_for_timeout(500)

        # 方式1: 使用 fill 方法(最简单最可靠)
        try:
            await input_field.fill('')
            await page.wait_for_timeout(300)
            await input_field.fill(new_tag)
            await page.wait_for_timeout(1000)
        except Exception as e:
            log(f"fill 方法失败: {str(e)}", "WARNING")

        # 验证填入是否成功
        filled_value = await input_field.input_value()
        log(f"第一次填入后的值: '{filled_value}'", "INFO")

        # 如果不匹配,尝试方式2: 使用键盘操作
        if filled_value != new_tag:
            log(f"第一次填入不完整,尝试键盘方式", "WARNING")

            # 点击聚焦
            await input_field.click(click_count=3)
            await page.wait_for_timeout(300)

            # macOS 使用 Meta+A, 其他系统使用 Control+A
            # Playwright 的 Meta 键在 macOS 上对应 Command
            try:
                await page.keyboard.press('Meta+A')  # macOS: Command+A
            except:
                await page.keyboard.press('Control+A')  # Windows/Linux

            await page.keyboard.press('Backspace')
            await page.wait_for_timeout(300)

            # 再次验证已清空
            current_value = await input_field.input_value()
            log(f"清空后的值: '{current_value}'", "INFO")

            # 逐字输入
            log(f"开始逐字输入: {new_tag}", "INFO")
            await page.keyboard.type(new_tag, delay=100)
            await page.wait_for_timeout(1000)

            # 再次验证
            filled_value = await input_field.input_value()
            log(f"键盘输入后的值: '{filled_value}'", "INFO")

        # 最终验证
        if filled_value != new_tag:
            log(f"错误: 版本号填入失败!", "ERROR")
            log(f"  期望: {new_tag}", "ERROR")
            log(f"  实际: {filled_value}", "ERROR")
            await take_screenshot(page, "input_value_mismatch")
            raise Exception(f"版本号填入失败: 期望 '{new_tag}', 实际 '{filled_value}'")

        log(f"✅ 成功填入新版本: {filled_value}", "SUCCESS")

        # 6. 点击【确定】按钮
        log("点击【确定】按钮...", "PROGRESS")

        # 尝试多种方式点击确定按钮
        button_clicked = False

        # 方式1: 通过弹窗内的"确定"按钮
        try:
            confirm_button = page.locator('.next-dialog >> button:has-text("确定")').first
            await confirm_button.wait_for(state='visible', timeout=5000)
            await confirm_button.click(timeout=5000)
            button_clicked = True
            log("成功点击确定按钮", "SUCCESS")
        except Exception as e:
            log(f"方式1点击失败: {str(e)}", "WARNING")

        # 方式2: 通过任何包含"确定"文字的按钮
        if not button_clicked:
            try:
                confirm_button = page.get_by_text("确定", exact=True).first
                await confirm_button.click(timeout=5000)
                button_clicked = True
                log("成功点击确定按钮(方式2)", "SUCCESS")
            except Exception as e:
                log(f"方式2点击失败: {str(e)}", "WARNING")

        if not button_clicked:
            await take_screenshot(page, "cannot_click_confirm")
            raise Exception("无法点击确定按钮")

        # 7. 等待弹窗关闭
        try:
            await page.wait_for_selector('text=调整镜像版本', state='hidden', timeout=config.OPERATION_TIMEOUT)
            log("镜像版本更新成功!", "SUCCESS")
        except PlaywrightTimeoutError:
            # 弹窗未关闭,可能更新失败
            log("警告: 弹窗未关闭,可能更新失败", "WARNING")
            await take_screenshot(page, "update_dialog_not_closed")

            # 检查是否有错误提示
            error_message = await page.locator('.next-message-error, .next-feedback-error').count()
            if error_message > 0:
                error_text = await page.locator('.next-message-error, .next-feedback-error').first.inner_text()
                raise Exception(f"更新失败: {error_text}")

            raise Exception("弹窗未关闭,更新状态未知")

    except PlaywrightTimeoutError as e:
        log(f"操作超时: {str(e)}", "ERROR")
        await take_screenshot(page, "k8s_timeout")
        raise Exception(f"K8s 操作超时: {str(e)}")

    except Exception as e:
        log(f"K8s 操作失败: {str(e)}", "ERROR")
        await take_screenshot(page, "k8s_error")
        raise
