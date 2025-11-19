import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """应用配置类"""
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-for-development')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    TEMPLATES_AUTO_RELOAD = True
    
    # 数据库配置
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '123456')
    DB_NAME = os.environ.get('DB_NAME', 'music')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    
    # 网易云音乐API配置
    NETEASE_MUSIC_AES_KEY = os.environ.get('NETEASE_MUSIC_AES_KEY', 'e82ckenh8dichen8').encode()
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'app.log')

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    
class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    
class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DB_NAME = os.environ.get('TEST_DB_NAME', 'analysis_test')

# 根据环境变量选择配置
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

# 获取当前配置
current_config = config_by_name.get(os.environ.get('FLASK_ENV', 'development'))