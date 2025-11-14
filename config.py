"""
配置管理模块
从环境变量读取配置,支持前端/后端、测试/生产多环境
"""

import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


# ==================== 镜像仓库配置 ====================
IMAGE_REGISTRY = os.getenv('IMAGE_REGISTRY', 'registry.wuxi.epartical.com:10443')
IMAGE_NAMESPACE = os.getenv('IMAGE_NAMESPACE', 'javaly')

# ==================== 云效界面配置 ====================
YUNXIAO_LOG_EXPAND_TEXT = os.getenv('YUNXIAO_LOG_EXPAND_TEXT', '镜像构建并推送')


# ==================== K8s 登录凭证 ====================
K8S_ENV_CREDENTIALS = {
    'test': {
        'username': os.getenv('K8S_DEV_USERNAME', ''),
        'password': os.getenv('K8S_DEV_PASSWORD', ''),
    },
    'prod': {
        'username': os.getenv('K8S_PROD_USERNAME', ''),
        'password': os.getenv('K8S_PROD_PASSWORD', ''),
    },
}


# ==================== 前端配置 ====================
FRONTEND_CONFIG = {
    # 云效运行（仅构建，不部署）
    'build': {
        'yunxiao_url': os.getenv('FRONTEND_TEST_YUNXIAO_URL', ''),
        'k8s_url': '',  # 不更新 K8s
        'tag_pattern': os.getenv('FRONTEND_TEST_TAG_PATTERN', r'javaly/jpms-web:(dev-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})'),
        'k8s_username': '',
        'k8s_password': '',
    },
    # 测试环境
    'test': {
        'yunxiao_url': os.getenv('FRONTEND_TEST_YUNXIAO_URL', ''),
        'k8s_url': os.getenv('FRONTEND_TEST_K8S_URL', ''),
        'tag_pattern': os.getenv('FRONTEND_TEST_TAG_PATTERN', r'javaly/jpms-web:(dev-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})'),
        'k8s_username': K8S_ENV_CREDENTIALS['test']['username'],
        'k8s_password': K8S_ENV_CREDENTIALS['test']['password'],
    },
    # 生产环境
    'prod': {
        'yunxiao_url': os.getenv('FRONTEND_PROD_YUNXIAO_URL', ''),
        'k8s_url': os.getenv('FRONTEND_PROD_K8S_URL', ''),
        'tag_pattern': os.getenv('FRONTEND_PROD_TAG_PATTERN', r'javaly/jpms-web:(prod-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})'),
        'k8s_username': K8S_ENV_CREDENTIALS['prod']['username'],
        'k8s_password': K8S_ENV_CREDENTIALS['prod']['password'],
    }
}


# ==================== 后端配置(预留) ====================
BACKEND_CONFIG = {
    # 云效运行（仅构建，不部署）
    'build': {
        'yunxiao_url': os.getenv('BACKEND_TEST_YUNXIAO_URL', ''),
        'k8s_url': '',  # 不更新 K8s
        'tag_pattern': os.getenv(
            'BACKEND_TEST_TAG_PATTERN',
            r'javaly/spms-server:(dev-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})',
        ),
        'log_button_index': int(os.getenv('BACKEND_TEST_LOG_INDEX', '0')),
        'log_job_keyword': os.getenv('BACKEND_TEST_LOG_JOB', 'Java 构建Docker镜像并推送镜像仓库'),
        'k8s_username': '',
        'k8s_password': '',
    },
    # 测试环境
    'test': {
        'yunxiao_url': os.getenv('BACKEND_TEST_YUNXIAO_URL', ''),
        'k8s_url': os.getenv('BACKEND_TEST_K8S_URL', ''),
        'tag_pattern': os.getenv(
            'BACKEND_TEST_TAG_PATTERN',
            r'javaly/spms-server:(dev-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})',
        ),
        'log_button_index': int(os.getenv('BACKEND_TEST_LOG_INDEX', '0')),
        'log_job_keyword': os.getenv('BACKEND_TEST_LOG_JOB', 'Java 构建Docker镜像并推送镜像仓库'),
        'k8s_username': K8S_ENV_CREDENTIALS['test']['username'],
        'k8s_password': K8S_ENV_CREDENTIALS['test']['password'],
    },
    # 生产环境
    'prod': {
        'yunxiao_url': os.getenv('BACKEND_PROD_YUNXIAO_URL', ''),
        'k8s_url': os.getenv('BACKEND_PROD_K8S_URL', ''),
        'tag_pattern': os.getenv(
            'BACKEND_PROD_TAG_PATTERN',
            r'javaly/spms-server:(prod-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})',
        ),
        'log_button_index': int(os.getenv('BACKEND_PROD_LOG_INDEX', '1')),
        'log_job_keyword': os.getenv('BACKEND_PROD_LOG_JOB', 'Java生产环境构建'),
        'k8s_username': K8S_ENV_CREDENTIALS['prod']['username'],
        'k8s_password': K8S_ENV_CREDENTIALS['prod']['password'],
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
HEADLESS = True

# 失败时是否自动截图
SCREENSHOT_ON_ERROR = True

# Cookie 存储文件路径
AUTH_FILE = "auth.json"

# 截图保存目录
SCREENSHOT_DIR = "screenshots"

# 日志保存目录
LOG_DIR = "logs"

# 默认凭证(与旧逻辑兼容,运行时由 TaskScheduler 设置)
K8S_USERNAME = FRONTEND_CONFIG['test']['k8s_username']
K8S_PASSWORD = FRONTEND_CONFIG['test']['k8s_password']
