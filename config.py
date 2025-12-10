import os
from datetime import timedelta
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """应用配置类"""
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-for-development')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    TESTING = False
    TEMPLATES_AUTO_RELOAD = True
    
    # Session配置
    PERMANENT_SESSION_LIFETIME = timedelta(days=int(os.environ.get('SESSION_LIFETIME_DAYS', 7)))  # 从环境变量读取session存活时间，默认7天
    SESSION_PERMANENT = True  # 启用持久化session
    
    # 服务器配置
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # 数据库配置
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '123456')
    DB_NAME = os.environ.get('DB_NAME', 'music')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    
    # 网易云音乐API配置
    NETEASE_MUSIC_AES_KEY = os.environ.get('NETEASE_MUSIC_AES_KEY', 'e82ckenh8dichen8').encode()
    # 网易云音乐Cookie配置
    NETEASE_MUSIC_COOKIE = os.environ.get('NETEASE_MUSIC_COOKIE', '')
    # 默认音质配置
    DEFAULT_MUSIC_QUALITY = os.environ.get('DEFAULT_MUSIC_QUALITY', 'standard')
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', 1024 * 1024 * 5))  # 默认5MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 30))  # 默认保留30个备份
    
    # 防护扫描配置
    # IP访问频率限制
    IP_RATE_LIMIT_ENABLED = os.environ.get('IP_RATE_LIMIT_ENABLED', 'True').lower() in ('true', '1', 't')
    IP_RATE_LIMIT = int(os.environ.get('IP_RATE_LIMIT', 100))  # 每个IP每分钟最大请求数
    IP_RATE_LIMIT_WINDOW = int(os.environ.get('IP_RATE_LIMIT_WINDOW', 60))  # 时间窗口（秒）
    # 恶意请求检测
    MALICIOUS_REQUEST_DETECTION = os.environ.get('MALICIOUS_REQUEST_DETECTION', 'True').lower() in ('true', '1', 't')
    # SQL注入检测正则
    SQL_INJECTION_PATTERNS = [
        r'(?:\'|\")(?:\s|\t|\r|\n)*(?:and|or|xor|not)(?:\s|\t|\r|\n)*(?:\'|\")',
        r'(?:\'|\")(?:\s|\t|\r|\n)*(?:select|insert|update|delete|drop|create|alter)(?:\s|\t|\r|\n)',
        r'(?:\'|\")(?:\s|\t|\r|\n)*(?:--|#|/\*|\*/)',
        r'(?:union|all)(?:\s|\t|\r|\n)*(?:select|insert|update|delete|drop|create|alter)',
        r'(?:\'|\")(?:\s|\t|\r|\n)*(?:exec|execute|xp_cmdshell|sp_executesql)',
        r'(?:\'|\")(?:\s|\t|\r|\n)*(?:into|from|where|having|group by|order by)(?:\s|\t|\r|\n)*(?:\'|\")'
    ]
    # XSS检测正则
    XSS_PATTERNS = [
        r'<(?:script|iframe|object|embed|form|input|textarea|button|select|option|link|meta|style|img)(?:\s|\t|\r|\n)*>',
        r'(?:onload|onunload|onerror|onclick|onmouseover|onmouseout|onkeydown|onkeyup|onkeypress)(?:\s|\t|\r|\n)*=',
        r'javascript:(?:[^\s]+)',
        r'vbscript:(?:[^\s]+)',
        r'expression\s*\(',
        r'data:\s*(?:image|text)/(?:png|jpg|jpeg|gif|html|javascript)(?:[^\s]+)'
    ]
    # 异常User-Agent检测
    ABNORMAL_UA_PATTERNS = [
        r'(?:bot|crawler|spider|scraper|harvester|checker)',
        r'(?:curl|wget|httpie|postman|insomnia)',
        r'(?:python-requests|go-http-client|java-http-client)',
        r'(?:.*\.exe|.*\.bat|.*\.sh|.*\.py)'
    ]
    # 拦截特定扫描User-Agent关键字
    BLOCK_UA_KEYWORDS = os.environ.get('BLOCK_UA_KEYWORDS', 'l9scan,leakix,nmap,masscan,sqlmap').split(',')
    # 白名单IP列表
    IP_WHITELIST = [ip.strip() for ip in os.environ.get('IP_WHITELIST', '').split(',') if ip.strip()]
    # 黑名单IP列表
    IP_BLACKLIST = [ip.strip() for ip in os.environ.get('IP_BLACKLIST', '').split(',') if ip.strip()]
    # 超时设置
    REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', 30))  # 单个请求最大超时时间（秒）

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
    
class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = False
    DB_NAME = os.environ.get('TEST_DB_NAME', 'analysis_test')
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARNING')

# 根据环境变量选择配置
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

# 获取当前配置
current_config = config_by_name.get(os.environ.get('FLASK_ENV', 'development'))