"""
工具模块: 日志、截图等辅助功能
"""
import os
from datetime import datetime
from playwright.async_api import Page
import config


def log(message: str, level: str = "INFO"):
    """
    打印带时间戳的日志

    Args:
        message: 日志消息
        level: 日志级别 (INFO, SUCCESS, ERROR, WARNING)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 根据级别选择emoji
    emoji_map = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "ERROR": "❌",
        "WARNING": "⚠️",
        "PROGRESS": "▶️",
        "WAITING": "⏳"
    }

    emoji = emoji_map.get(level, "📝")
    print(f"[{timestamp}] {emoji} {message}")


async def take_screenshot(page: Page, name: str = "error") -> str:
    """
    截图并保存到 screenshots 目录

    Args:
        page: Playwright Page 对象
        name: 截图文件名前缀

    Returns:
        截图文件路径
    """
    # 确保目录存在
    os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)

    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name}_{timestamp}.png"
    filepath = os.path.join(config.SCREENSHOT_DIR, filename)

    # 截图
    await page.screenshot(path=filepath, full_page=True)
    log(f"截图已保存: {filepath}", "INFO")

    return filepath


def format_duration(seconds: float) -> str:
    """
    格式化时间长度

    Args:
        seconds: 秒数

    Returns:
        格式化后的字符串 (例: "2分30秒")
    """
    if seconds < 60:
        return f"{int(seconds)}秒"

    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)

    if remaining_seconds == 0:
        return f"{minutes}分钟"

    return f"{minutes}分{remaining_seconds}秒"
