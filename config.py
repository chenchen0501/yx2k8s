"""
配置管理模块
从环境变量读取配置,支持前端/后端、测试/生产多环境
"""

import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


# ==================== 前端配置 ====================
FRONTEND_CONFIG = {
    # 测试环境
    'test': {
        'yunxiao_url': os.getenv('FRONTEND_TEST_YUNXIAO_URL', ''),
        'k8s_url': os.getenv('FRONTEND_TEST_K8S_URL', ''),
        'tag_pattern': os.getenv('FRONTEND_TEST_TAG_PATTERN', r'javaly/jpms-web:(dev-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})'),
    },
    # 生产环境
    'prod': {
        'yunxiao_url': os.getenv('FRONTEND_PROD_YUNXIAO_URL', ''),
        'k8s_url': os.getenv('FRONTEND_PROD_K8S_URL', ''),
        'tag_pattern': os.getenv('FRONTEND_PROD_TAG_PATTERN', r'javaly/jpms-web:(prod-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})'),
    }
}


# ==================== 后端配置(预留) ====================
BACKEND_CONFIG = {
    # 测试环境
    'test': {
        'yunxiao_url': os.getenv('BACKEND_TEST_YUNXIAO_URL', ''),
        'k8s_url': os.getenv('BACKEND_TEST_K8S_URL', ''),
        'tag_pattern': os.getenv('BACKEND_TEST_TAG_PATTERN', ''),
    },
    # 生产环境
    'prod': {
        'yunxiao_url': os.getenv('BACKEND_PROD_YUNXIAO_URL', ''),
        'k8s_url': os.getenv('BACKEND_PROD_K8S_URL', ''),
        'tag_pattern': os.getenv('BACKEND_PROD_TAG_PATTERN', ''),
    }
}


# ==================== 兼容旧代码的变量(默认使用前端测试环境) ====================
YUNXIAO_URL = FRONTEND_CONFIG['test']['yunxiao_url']
K8S_URL = FRONTEND_CONFIG['test']['k8s_url']
TAG_PATTERN = FRONTEND_CONFIG['test']['tag_pattern']


# ==================== 超时配置 ====================
# 构建超时时间(毫秒) - 5分钟
BUILD_TIMEOUT = 300000

# 页面操作超时时间(毫秒) - 30秒
OPERATION_TIMEOUT = 30000

# 页面加载超时时间(毫秒) - 1分钟
PAGE_LOAD_TIMEOUT = 60000


# ==================== 浏览器配置 ====================
# 是否使用无头模式(True=后台运行, False=显示浏览器窗口)
HEADLESS = False

# 失败时是否自动截图
SCREENSHOT_ON_ERROR = True

# Cookie 存储文件路径
AUTH_FILE = "auth.json"

# 截图保存目录
SCREENSHOT_DIR = "screenshots"

# 日志保存目录
LOG_DIR = "logs"
