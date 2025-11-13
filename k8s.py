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
        await page.wait_for_timeout(500)
        if not await _ensure_k8s_logged_in(page):
            raise Exception("自动登录 K8s 失败,请检查账号密码或页面是否有额外校验")

        # 2. 点击【调整镜像版本】按钮
        log("点击【调整镜像版本】按钮...", "PROGRESS")
        # 关闭可能遮挡的版本升级提示
        try:
            close_upgrade = page.locator('div:has-text("检测到新版本") >> .. >> button, .el-message__closeBtn, .next-message-close').first
            if await close_upgrade.is_visible():
                await close_upgrade.click()
                await page.wait_for_timeout(200)
        except:
            pass

        # 主按钮与备用选择器
        click_success = False
        button_selectors = [
            'button:has-text("调整镜像版本")',
            '//*[@role="dialog"]//button[span[contains(text(),"调整镜像版本")]]',
            'text=调整镜像版本 >> xpath=ancestor::button',
        ]
        for sel in button_selectors:
            try:
                btn = page.locator(sel).first
                await btn.wait_for(state='visible', timeout=3000)
                await btn.scroll_into_view_if_needed()
                await page.wait_for_timeout(100)
                await btn.click(timeout=3000)
                click_success = True
                break
            except Exception:
                continue

        # 兜底使用 force 点击
        if not click_success:
            try:
                btn = page.locator('button:has-text("调整镜像版本")').first
                await btn.scroll_into_view_if_needed()
                await btn.click(timeout=2000, force=True)
                click_success = True
            except Exception as e:
                log(f"点击【调整镜像版本】失败: {str(e)}", "ERROR")
                await take_screenshot(page, "click_adjust_button_failed")
                raise

        # 3. 等待弹窗出现
        await page.wait_for_selector('.next-dialog:has-text("调整镜像版本"), .el-dialog:has-text("调整镜像版本")',
                                     state='visible', timeout=config.OPERATION_TIMEOUT)
        log("调整镜像版本弹窗已打开", "INFO")

        # 4. 定位"新版本"输入框
        log(f"填入新版本号: {new_tag}", "PROGRESS")

        # 尝试多种方式定位输入框
        input_field = None

        # 优先：锁定包含目标容器名的行，再在该行的最后一列找输入框
        try:
            row = page.locator('tr.el-table__row').filter(has_text='jpms-web').first
            await row.wait_for(state='visible', timeout=4000)
            candidate = row.locator('td').last.locator('input.el-input__inner')
            await candidate.wait_for(state='visible', timeout=2000)
            input_field = candidate
            log("通过包含 'jpms-web' 的表格行定位到输入框", "INFO")
        except Exception:
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

        button_clicked = False
        try:
            # 锁定当前可见弹窗
            dialog = page.locator('.next-dialog:visible, .el-dialog:visible').last
            await dialog.wait_for(state='visible', timeout=5000)

            # 多套选择器（Next UI / Element Plus / 文本变体）
            confirm_selectors = [
                'button:has-text("确定")',
                'button:has-text("确 定")',
                '.el-dialog__footer button.el-button--primary',
                '.el-dialog__footer .el-button--primary',
                '.next-dialog-footer .next-btn-primary',
                'footer .next-btn-primary',
            ]

            for sel in confirm_selectors:
                try:
                    btn = dialog.locator(sel).first
                    if await btn.count() == 0:
                        continue
                    await btn.scroll_into_view_if_needed()
                    await btn.wait_for(state='visible', timeout=2000)
                    # 避免禁用状态
                    is_disabled = await btn.get_attribute('disabled')
                    if is_disabled is not None:
                        continue
                    await btn.click(timeout=3000)
                    button_clicked = True
                    log("成功点击确定按钮", "SUCCESS")
                    break
                except Exception:
                    continue

            # 兜底1：在输入框上回车提交
            if not button_clicked:
                try:
                    await input_field.focus()
                    await page.keyboard.press('Enter')
                    button_clicked = True
                    log("通过回车提交", "INFO")
                except Exception:
                    pass

            # 兜底2：使用原生 click
            if not button_clicked:
                try:
                    btn = dialog.locator('button:has-text("确定"), button:has-text("确 定")').first
                    await btn.wait_for(state='visible', timeout=2000)
                    await btn.evaluate('el => el.click()')
                    button_clicked = True
                    log("使用原生 click 触发确定", "INFO")
                except Exception:
                    pass
        except Exception as e:
            log(f"查找确定按钮异常: {str(e)}", "WARNING")

        if not button_clicked:
            await take_screenshot(page, "cannot_click_confirm")
            raise Exception("无法点击确定按钮")

        # 二次确认弹框（如"确认调整镜像版本"）
        try:
            confirm_dialog = page.locator(
                '.next-dialog:has-text("确认调整镜像版本"), .el-dialog:has-text("确认调整镜像版本")'
            ).first
            await confirm_dialog.wait_for(state='visible', timeout=2000)
            log("检测到二次确认弹框，执行确认...", "INFO")

            confirm_again_selectors = [
                'button:has-text("确定")',
                'button:has-text("确 定")',
                '.el-dialog__footer .el-button--primary',
                '.next-dialog-footer .next-btn-primary',
            ]
            confirm_again_clicked = False

            for sel in confirm_again_selectors:
                try:
                    btn = confirm_dialog.locator(sel).first
                    if await btn.count() == 0:
                        continue
                    await btn.scroll_into_view_if_needed()
                    await btn.wait_for(state='visible', timeout=1000)
                    await btn.click(timeout=2000)
                    confirm_again_clicked = True
                    log("二次确认已点击确定", "INFO")
                    break
                except Exception:
                    continue

            if not confirm_again_clicked:
                # 兜底使用原生 click
                btn = confirm_dialog.locator('button:has-text("确定"), button:has-text("确 定")').first
                await btn.wait_for(state='visible', timeout=1000)
                await btn.evaluate('el => el.click()')
                log("二次确认通过原生 click 完成", "INFO")

            await page.wait_for_selector(
                '.next-dialog:has-text("确认调整镜像版本"), .el-dialog:has-text("确认调整镜像版本")',
                state='hidden',
                timeout=5000,
            )
        except PlaywrightTimeoutError:
            pass
        except Exception as e:
            log(f"二次确认弹框处理失败: {str(e)}", "WARNING")

        # Element Plus MessageBox 变体（.el-message-box）
        try:
            msg_box = page.locator('.el-message-box:visible').last
            await msg_box.wait_for(state='visible', timeout=2000)
            log("检测到 Element Plus MessageBox，执行确认...", "INFO")
            primary_btn = msg_box.locator('.el-message-box__btns .el-button--primary').first
            await primary_btn.wait_for(state='visible', timeout=2000)
            try:
                await primary_btn.click(timeout=2000)
            except Exception:
                await primary_btn.evaluate('el => el.click()')
            await page.wait_for_selector('.el-message-box:visible', state='hidden', timeout=5000)
        except PlaywrightTimeoutError:
            pass
        except Exception as e:
            log(f"MessageBox 确认失败: {str(e)}", "WARNING")

        # 7. 等待弹窗关闭
        try:
            await page.wait_for_selector('.next-dialog:has-text("调整镜像版本"), .el-dialog:has-text("调整镜像版本")',
                                         state='hidden', timeout=config.OPERATION_TIMEOUT)
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


async def _ensure_k8s_logged_in(page: Page, allow_retry: bool = True) -> bool:
    """
    确保已登录 K8s 控制台,必要时执行自动登录

    Args:
        page: 当前页面
        allow_retry: 自动登录失败时是否允许返回 False (用于手动登录后的再次校验)
    """
    if await _is_k8s_console_loaded(page):
        return True

    login_form = page.locator('form.el-form').first
    try:
        if await login_form.count() == 0:
            return True
        if not await login_form.is_visible():
            return await _is_k8s_console_loaded(page)
    except PlaywrightTimeoutError:
        return await _is_k8s_console_loaded(page)
    except Exception:
        return await _is_k8s_console_loaded(page)

    if not config.K8S_USERNAME or not config.K8S_PASSWORD:
        log("检测到登录表单,但未配置 K8s 账号密码,无法自动登录", "WARNING")
        return False if allow_retry else False

    log("检测到登录表单,尝试自动填充账号密码...", "INFO")

    try:
        username_input = login_form.locator('input[placeholder="请输入用户名"]').first
        password_input = login_form.locator('input[placeholder="请输入密码"]').first
        login_button = login_form.locator('button.el-button--primary').first

        await username_input.wait_for(state='visible', timeout=5000)
        await password_input.wait_for(state='visible', timeout=5000)
        await login_button.wait_for(state='visible', timeout=5000)

        await username_input.fill(config.K8S_USERNAME)
        await password_input.fill(config.K8S_PASSWORD)

        await login_button.click()
        await page.wait_for_load_state('networkidle')

        try:
            await login_form.wait_for(state='hidden', timeout=5000)
        except PlaywrightTimeoutError:
            pass  # 有些环境登录后表单仍留在 DOM 中,改为后续判定

        if await _is_k8s_console_loaded(page):
            log("自动登录成功", "SUCCESS")
            return True

        await login_form.wait_for(state='hidden', timeout=config.PAGE_LOAD_TIMEOUT)
        if await _is_k8s_console_loaded(page):
            log("自动登录成功", "SUCCESS")
            return True
    except PlaywrightTimeoutError:
        log("自动登录后仍检测到登录表单,可能是凭证错误或需要额外验证", "ERROR")
    except Exception as exc:
        log(f"自动登录失败: {str(exc)}", "ERROR")

    if allow_retry:
        await take_screenshot(page, "k8s_auto_login_failed")
    return False


async def _is_k8s_console_loaded(page: Page) -> bool:
    """判断是否已进入 K8s 控制台页面"""
    selectors = [
        'text=Deployment',
        'button:has-text("调整镜像版本")',
        'text=应用操作',
        '.el-menu:has-text("工作负载")',
        'div:has-text("kuboard")',
    ]
    for sel in selectors:
        locator = page.locator(sel).first
        try:
            if await locator.count() > 0 and await locator.is_visible():
                return True
        except Exception:
            continue
    return False
