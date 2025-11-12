"""
配置管理模块
"""

# ==================== 云效配置 ====================
# 云效 Pipeline URL
YUNXIAO_URL = "https://flow.aliyun.com/pipelines/4368447/current"

# 版本号提取正则表达式
# 匹配: javaly/jpms-web:dev-2025-11-12-14-20-32
TAG_PATTERN = r'javaly/jpms-web:(dev-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})'


# ==================== K8s 配置 ====================
# K8s Deployment 详情页 URL
K8S_URL = "https://k8s.dev.wuxi.epartical.com:40022/kubernetes/ops/namespace/jpms/workload/view/Deployment/jpms-web"


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
