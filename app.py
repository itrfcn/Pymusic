import os
import re
import logging
from typing import List
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template, request, session, redirect, url_for, abort

# 导入项目依赖
from config import current_config
from apps.music import music  # 音乐模块蓝图
from apps.user import user  # 用户模块蓝图
from apps.clean_history_data import register_cleanup_hook  # 历史数据清理钩子


# ======================== 日志辅助函数 ========================
def log_request_details(logger, request, level, message, **kwargs):
    """记录请求详细信息的辅助函数
    
    Args:
        logger: 日志记录器对象
        request: Flask请求对象
        level: 日志级别 ('debug', 'info', 'warning', 'error', 'critical')
        message: 日志消息内容
        **kwargs: 额外的日志参数
    """
    # 构建请求详情字符串
    request_info = {
        'IP': request.remote_addr,
        '方法': request.method,
        '路径': request.path,
        '用户代理': request.headers.get('User-Agent', '未知')
    }
    
    # 格式化请求信息
    request_details = ' | '.join([f"{k}: {v}" for k, v in request_info.items()])
    full_message = f"{message} [{request_details}]"
    
    # 根据级别记录日志
    log_method = getattr(logger, level)
    log_method(full_message, **kwargs)

# ======================== 可变配置 ========================
# 公开页面列表（无需登录即可访问）
PUBLIC_PAGES: List[str] = ['discover', 'rank', 'doc-163', 'about']
# 受保护页面列表（需要登录才能访问）
PROTECTED_PAGES: List[str] = ['history', 'playlist_detail']
# 所有允许访问的页面
ALLOWED_PAGES: List[str] = PUBLIC_PAGES + PROTECTED_PAGES
# 允许访问的部分页面（与主页面列表保持一致）
ALLOWED_PARTIALS: List[str] = ALLOWED_PAGES
# 页面片段名称验证正则表达式（允许字母、数字、短横线和下划线）
PARTIAL_CHAR_PATTERN: re.Pattern = re.compile(r'^[a-zA-Z0-9\-_]+$')


# ======================== 应用工厂函数 ========================
def create_app(config_name=None) -> Flask:
    """Flask应用工厂函数
    
    负责创建和配置Flask应用实例
    """
    # 创建临时logger用于初始化过程
    temp_logger = logging.getLogger('app_init')
    temp_logger.setLevel(logging.INFO)
    temp_handler = logging.StreamHandler()
    temp_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    temp_logger.addHandler(temp_handler)
    
    # 记录应用开始初始化
    temp_logger.info("开始初始化应用...")
    
    # 创建Flask应用实例
    app = Flask(__name__)
    
    # 1. 加载配置
    try:
        app.config.from_object(config_name)
        temp_logger.info(f"配置加载成功: {config_name.__name__ if config_name else '默认配置'}")
    except Exception as e:
        temp_logger.error(f"配置加载失败: {str(e)}")
        raise
    
    # 生产环境安全校验
    if not app.debug and not app.testing and not app.config.get('SECRET_KEY'):
        error_msg = "生产环境必须配置 SECRET_KEY（通过环境变量或配置文件）"
        temp_logger.error(error_msg)
        raise ValueError(error_msg)
    
    # 2. 配置日志系统
    temp_logger.info("正在配置日志系统...")
    configure_logging(app)
    
    # 移除临时logger处理器
    temp_logger.removeHandler(temp_handler)
    
    # 3. 注册蓝图（模块化管理路由）
    try:
        # 添加请求日志中间件到所有Blueprint
        def blueprint_request_logger(blueprint_name):
            @app.before_request
            def log_request():
                # 只处理当前Blueprint的请求
                if request.path.startswith(f'/{blueprint_name}'):
                    log_request_details(app.logger, request, 'info', f"[Blueprint:{blueprint_name}] 请求开始")
            
            @app.after_request
            def log_response(response):
                # 只处理当前Blueprint的请求
                if request.path.startswith(f'/{blueprint_name}'):
                    log_request_details(app.logger, request, 'info', 
                                      f"[Blueprint:{blueprint_name}] 请求结束 | 状态码: {response.status_code}")
                return response
            return log_request, log_response
        
        # 为music模块添加日志中间件
        blueprint_request_logger('music')
        # 为user模块添加日志中间件
        blueprint_request_logger('user')
        
        # 注册蓝图
        app.register_blueprint(music, url_prefix='/music')  # 音乐相关API路由
        app.register_blueprint(user, url_prefix='/user')    # 用户相关API路由
        app.logger.info("蓝图注册完成并添加日志中间件")
    except Exception as e:
        app.logger.error("蓝图注册失败", exc_info=True)
        raise
    
    # 4. 注册数据清理钩子（定时清理过期的播放历史数据）
    try:
        register_cleanup_hook(app)
        app.logger.info("数据清理钩子注册完成")
    except Exception as e:
        app.logger.error("数据清理钩子注册失败", exc_info=True)
        raise
    
    # 5. 定义核心路由
    try:
        _register_routes(app)
        app.logger.info(f"核心路由注册完成，当前路由规则数: {len(app.url_map._rules)}")
    except Exception as e:
        app.logger.error("核心路由注册失败", exc_info=True)
        raise
    
    # 记录应用初始化完成
    app.logger.info("应用初始化完成")
    app.logger.info(f"当前环境: {'开发' if app.debug else '生产'}")
    app.logger.info(f"调试模式: {app.debug}")
    
    return app


def _register_routes(app: Flask) -> None:
    """注册应用路由
    
    将所有路由注册到Flask应用实例中
    """
    # 记录路由注册开始
    app.logger.info("开始注册应用路由...")
    
    # 记录允许的页面列表信息
    app.logger.debug(f"允许访问的页面: {ALLOWED_PAGES}")
    app.logger.debug(f"允许访问的页面片段: {ALLOWED_PARTIALS}")
    app.logger.debug(f"受保护的页面: {PROTECTED_PAGES}")
    
    # 首页路由
    @app.route('/')
    @app.route('/<page_name>')
    def index(page_name: str = 'discover') -> str:
        """SPA应用入口路由
        
        处理主页面访问，支持登录注册页面和权限控制
        """
        # 登录注册页面路由
        if page_name == 'login':
            log_request_details(app.logger, request, 'info', f"用户访问登录页面")
            return render_template('user/login.html')
        if page_name == 'register':
            log_request_details(app.logger, request, 'info', f"用户访问注册页面")
            return render_template('user/register.html')

        # 无效页面兜底处理
        if page_name not in ALLOWED_PAGES:
            log_request_details(app.logger, request, 'warning', 
                               f"无效页面请求: {page_name}，已重定向至默认页面")
            page_name = 'discover'
        
        # 权限校验：未登录用户无法访问受保护页面
        if page_name in PROTECTED_PAGES and 'user_id' not in session:
            log_request_details(app.logger, request, 'info', 
                               f"未登录用户尝试访问受保护页面: {page_name}，已重定向至登录页")
            return redirect('/login')
        
        # 记录正常页面访问
        user_status = f"已登录(用户ID:{session.get('user_id')})" if 'user_id' in session else "未登录"
        log_request_details(app.logger, request, 'info', 
                           f"用户访问页面: {page_name} ({user_status})")
        
        # 渲染入口页面，传递页面标识和用户状态
        return render_template('index.html', page=page_name)
    

    # SPA页面片段加载路由(保护项目真实结构)
    @app.route('/index/<page>', methods=['GET'], strict_slashes=False)
    def partial(page: str = '') -> str:
        """SPA页面片段加载路由
        
        负责加载SPA应用的动态内容片段
        """
        # 1. 空片段请求拦截
        if not page:
            log_request_details(app.logger, request, 'warning', "空片段请求")
            abort(404)
        
        # 2. 页面名字符合法性验证（防止路径注入）
        if not PARTIAL_CHAR_PATTERN.match(page):
            log_request_details(app.logger, request, 'warning', 
                               f"非法页面片段字符: {page}（可能的路径注入尝试）")
            abort(404)
        
        # 3. 页面访问白名单验证
        if page not in ALLOWED_PARTIALS:
            log_request_details(app.logger, request, 'warning', 
                               f"禁止访问的页面片段: {page}")
            abort(404)
        
        # 4. 模板文件路径构建
        template_file: str = f'partials/{page}.html'
        template_abspath: str = os.path.join(
            app.template_folder,  # 使用Flask内置模板目录，避免硬编码错误
            'partials',
            f'{page}.html'
        )
        
        # 5. 模板文件存在性验证
        if not os.path.exists(template_abspath):
            log_request_details(app.logger, request, 'error', 
                               f"页面模板文件不存在: {template_file} (路径: {template_abspath})")
            abort(404)
        
        # 6. 记录正常访问日志
        log_request_details(app.logger, request, 'info', f"加载页面片段: {page}")
        
        # 7. 渲染页面片段并返回
        return render_template(template_file)
    
    @app.errorhandler(404)
    def not_found(error) -> tuple:
        """404错误处理
        
        根据请求类型返回不同格式的404响应
        """
        # 片段请求返回轻量级错误信息
        if request.path.startswith('/index/'):
            log_request_details(app.logger, request, 'warning', 
                               f"页面片段404: {request.path}")
            return (
                '<div style="color: #dc3545; margin: 20px; font-size: 16px;">' \
                '❌ 页面片段不存在或不允许访问' \
                '</div>',
                404
            )
        
        # 普通请求返回完整的404页面
        log_request_details(app.logger, request, 'warning', 
                           f"页面404: {request.path}")
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(error) -> tuple:
        """500服务器错误处理
        
        记录详细错误信息并返回友好的错误页面
        """
        # 记录完整错误信息（包含堆栈跟踪）
        log_request_details(app.logger, request, 'error', 
                           f"服务器内部错误: {str(error)}", 
                           exc_info=True)
        
        # 检查是否存在自定义500错误页面
        error_template_path = os.path.join(app.template_folder, '500.html')
        if os.path.exists(error_template_path):
            return render_template('500.html'), 500
        
        # 返回默认错误信息
        return '<h1>服务器内部错误，请稍后重试</h1>', 500


# ======================== 日志配置函数 ========================
def configure_logging(app: Flask) -> None:
    """
    配置应用日志系统
    
    针对不同环境优化日志格式和级别：
    - 开发环境：控制台详细日志，包含调试信息
    - 生产环境：文件日志（轮转）+ 控制台日志，更规范的格式
    """
    # 1. 配置werkzeug logger（禁用或自定义Flask的默认访问日志）
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.handlers.clear()  # 清除默认处理器
    
    # 生产环境完全禁用werkzeug默认日志，使用我们自己的日志系统
    if not app.debug and not app.testing:
        werkzeug_logger.setLevel(logging.CRITICAL)  # 只记录严重错误
    else:
        # 开发环境可以保留，但使用我们的格式
        werkzeug_handler = logging.StreamHandler()
        werkzeug_handler.setFormatter(logging.Formatter(
            '%(asctime)s [WERKZEUG] %(message)s'
        ))
        werkzeug_logger.addHandler(werkzeug_handler)
        werkzeug_logger.setLevel(logging.INFO)
    
    # 2. 清除应用日志现有处理器，避免重复
    app.logger.handlers.clear()
    
    # 2. 获取日志配置参数
    log_level: str = getattr(current_config, 'LOG_LEVEL', 'INFO')
    log_file: str = getattr(current_config, 'LOG_FILE', 'logs/app.log')
    log_max_bytes: int = getattr(current_config, 'LOG_MAX_BYTES', 1024 * 1024 * 5)  # 默认5MB
    log_backup_count: int = getattr(current_config, 'LOG_BACKUP_COUNT', 30)  # 默认保留30个备份
    
    # 3. 日志级别容错处理
    numeric_level: int = getattr(logging, log_level.upper(), logging.INFO)
    
    # 4. 开发/测试环境配置
    if app.debug or app.testing:
        # 增强的控制台日志格式 - 开发环境需要更多调试信息
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s [模块:%(module)s 函数:%(funcName)s 行:%(lineno)d]'
        ))
        console_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(console_handler)
        app.logger.setLevel(logging.DEBUG)
        
        app.logger.info("【开发环境】日志系统已配置完成 - 调试模式")
        return
    
    # 5. 生产环境配置
    try:
        # 5.1 创建日志目录
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # 5.2 文件日志处理器配置（按大小轮转）
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=log_max_bytes,
            backupCount=log_backup_count,
            encoding='utf-8'  # 强制UTF-8编码，确保中文正常显示
        )
        # 详细的文件日志格式 - 包含完整上下文信息
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)7s] [进程:%(process)d] [线程:%(threadName)s] ' \
            '[%(module)s:%(funcName)s:%(lineno)d] - %(message)s'
        ))
        file_handler.setLevel(numeric_level)
        
        # 5.3 控制台日志处理器配置（容器环境友好，日志级别可配置）
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s'
        ))
        console_handler.setLevel(numeric_level)
        
        # 5.4 注册日志处理器
        app.logger.addHandler(file_handler)
        app.logger.addHandler(console_handler)
        
        # 5.5 设置日志级别
        app.logger.setLevel(numeric_level)
        
        # 5.6 记录启动信息 - 更详细的环境信息
        app.logger.info(
            f"【系统启动】应用启动成功 | 环境：生产 | 日志级别：{log_level.upper()} "
            f"| 端口：{app.config.get('PORT', 5000)} | 主机：{app.config.get('HOST', '0.0.0.0')} "
            f"| 日志文件：{log_file} | 最大文件大小：{log_max_bytes/(1024*1024):.1f}MB "
            f"| 备份数量：{log_backup_count}"
        )
        
    except Exception as e:
        # 日志配置失败时，使用简单的控制台日志作为后备方案
        fallback_handler = logging.StreamHandler()
        fallback_handler.setFormatter(logging.Formatter(
            '%(asctime)s [ERROR] 日志配置失败: %(message)s'
        ))
        app.logger.addHandler(fallback_handler)
        app.logger.setLevel(logging.ERROR)
        app.logger.error(f"无法配置日志系统: {str(e)}")

# ======================== 应用实例创建 ========================
# 创建应用实例，根据环境变量自动选择配置
app = create_app(current_config)

# ======================== 应用启动入口 ========================
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',  # 允许所有网络接口访问
        port=app.config.get('PORT', 5000),  # 从配置读取端口
        debug=app.config.get('DEBUG', False)  # 调试模式（生产环境必须关闭）
    )


# ======================== 应用工厂函数 ========================
def create_app(config_name=None) -> Flask:
    """Flask应用工厂函数
    
    负责创建和配置Flask应用实例
    """
    # 创建临时logger用于初始化过程
    temp_logger = logging.getLogger('app_init')
    temp_logger.setLevel(logging.INFO)
    temp_handler = logging.StreamHandler()
    temp_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    temp_logger.addHandler(temp_handler)
    
    # 记录应用开始初始化
    temp_logger.info("开始初始化应用...")
    
    # 创建Flask应用实例
    app = Flask(__name__)
    
    # 1. 加载配置
    try:
        app.config.from_object(config_name)
        temp_logger.info(f"配置加载成功: {config_name.__name__ if config_name else '默认配置'}")
    except Exception as e:
        temp_logger.error(f"配置加载失败: {str(e)}")
        raise
    
    # 生产环境安全校验
    if not app.debug and not app.testing and not app.config.get('SECRET_KEY'):
        error_msg = "生产环境必须配置 SECRET_KEY（通过环境变量或配置文件）"
        temp_logger.error(error_msg)
        raise ValueError(error_msg)
    
    # 2. 配置日志系统
    temp_logger.info("正在配置日志系统...")
    configure_logging(app)
    
    # 移除临时logger处理器
    temp_logger.removeHandler(temp_handler)
    
    # 3. 注册蓝图（模块化管理路由）
    try:
        # 添加请求日志中间件到所有Blueprint
        def blueprint_request_logger(blueprint_name):
            @app.before_request
            def log_request():
                # 只处理当前Blueprint的请求
                if request.path.startswith(f'/{blueprint_name}'):
                    log_request_details(app.logger, request, 'info', f"[Blueprint:{blueprint_name}] 请求开始")
            
            @app.after_request
            def log_response(response):
                # 只处理当前Blueprint的请求
                if request.path.startswith(f'/{blueprint_name}'):
                    log_request_details(app.logger, request, 'info', 
                                      f"[Blueprint:{blueprint_name}] 请求结束 | 状态码: {response.status_code}")
                return response
            return log_request, log_response
        
        # 为music模块添加日志中间件
        blueprint_request_logger('music')
        # 为user模块添加日志中间件
        blueprint_request_logger('user')
        
        # 注册蓝图
        app.register_blueprint(music, url_prefix='/music')  # 音乐相关API路由
        app.register_blueprint(user, url_prefix='/user')    # 用户相关API路由
        app.logger.info("蓝图注册完成并添加日志中间件")
    except Exception as e:
        app.logger.error("蓝图注册失败", exc_info=True)
        raise
    
    # 4. 注册数据清理钩子（定时清理过期的播放历史数据）
    try:
        register_cleanup_hook(app)
        app.logger.info("数据清理钩子注册完成")
    except Exception as e:
        app.logger.error("数据清理钩子注册失败", exc_info=True)
        raise
    
    # 5. 定义核心路由
    try:
        _register_routes(app)
        app.logger.info(f"核心路由注册完成，当前路由规则数: {len(app.url_map._rules)}")
    except Exception as e:
        app.logger.error("核心路由注册失败", exc_info=True)
        raise
    
    # 记录应用初始化完成
    app.logger.info("应用初始化完成")
    app.logger.info(f"当前环境: {'开发' if app.debug else '生产'}")
    app.logger.info(f"调试模式: {app.debug}")
    
    return app


def _register_routes(app: Flask) -> None:
    """注册应用路由
    
    将所有路由注册到Flask应用实例中
    """
    # 记录路由注册开始
    app.logger.info("开始注册应用路由...")
    
    # 记录允许的页面列表信息
    app.logger.debug(f"允许访问的页面: {ALLOWED_PAGES}")
    app.logger.debug(f"允许访问的页面片段: {ALLOWED_PARTIALS}")
    app.logger.debug(f"受保护的页面: {PROTECTED_PAGES}")
    
    # 首页路由
    @app.route('/')
    @app.route('/<page_name>')
    def index(page_name: str = 'discover') -> str:
        """SPA应用入口路由
        
        处理主页面访问，支持登录注册页面和权限控制
        """
        # 登录注册页面路由
        if page_name == 'login':
            log_request_details(app.logger, request, 'info', f"用户访问登录页面")
            return render_template('user/login.html')
        if page_name == 'register':
            log_request_details(app.logger, request, 'info', f"用户访问注册页面")
            return render_template('user/register.html')

        # 无效页面兜底处理
        if page_name not in ALLOWED_PAGES:
            log_request_details(app.logger, request, 'warning', 
                               f"无效页面请求: {page_name}，已重定向至默认页面")
            page_name = 'discover'
        
        # 权限校验：未登录用户无法访问受保护页面
        if page_name in PROTECTED_PAGES and 'user_id' not in session:
            log_request_details(app.logger, request, 'info', 
                               f"未登录用户尝试访问受保护页面: {page_name}，已重定向至登录页")
            return redirect('/login')
        
        # 记录正常页面访问
        user_status = f"已登录(用户ID:{session.get('user_id')})" if 'user_id' in session else "未登录"
        log_request_details(app.logger, request, 'info', 
                           f"用户访问页面: {page_name} ({user_status})")
        
        # 渲染入口页面，传递页面标识和用户状态
        return render_template('index.html', page=page_name)
    

    # SPA页面片段加载路由(保护项目真实结构)
    @app.route('/index/<page>', methods=['GET'], strict_slashes=False)
    def partial(page: str = '') -> str:
        """SPA页面片段加载路由
        
        负责加载SPA应用的动态内容片段
        """
        # 1. 空片段请求拦截
        if not page:
            log_request_details(app.logger, request, 'warning', "空片段请求")
            abort(404)
        
        # 2. 页面名字符合法性验证（防止路径注入）
        if not PARTIAL_CHAR_PATTERN.match(page):
            log_request_details(app.logger, request, 'warning', 
                               f"非法页面片段字符: {page}（可能的路径注入尝试）")
            abort(404)
        
        # 3. 页面访问白名单验证
        if page not in ALLOWED_PARTIALS:
            log_request_details(app.logger, request, 'warning', 
                               f"禁止访问的页面片段: {page}")
            abort(404)
        
        # 4. 模板文件路径构建
        template_file: str = f'partials/{page}.html'
        template_abspath: str = os.path.join(
            app.template_folder,  # 使用Flask内置模板目录，避免硬编码错误
            'partials',
            f'{page}.html'
        )
        
        # 5. 模板文件存在性验证
        if not os.path.exists(template_abspath):
            log_request_details(app.logger, request, 'error', 
                               f"页面模板文件不存在: {template_file} (路径: {template_abspath})")
            abort(404)
        
        # 6. 记录正常访问日志
        log_request_details(app.logger, request, 'info', f"加载页面片段: {page}")
        
        # 7. 渲染页面片段并返回
        return render_template(template_file)
    
    @app.errorhandler(404)
    def not_found(error) -> tuple:
        """404错误处理
        
        根据请求类型返回不同格式的404响应
        """
        # 片段请求返回轻量级错误信息
        if request.path.startswith('/index/'):
            log_request_details(app.logger, request, 'warning', 
                               f"页面片段404: {request.path}")
            return (
                '<div style="color: #dc3545; margin: 20px; font-size: 16px;">' \
                '❌ 页面片段不存在或不允许访问' \
                '</div>',
                404
            )
        
        # 普通请求返回完整的404页面
        log_request_details(app.logger, request, 'warning', 
                           f"页面404: {request.path}")
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(error) -> tuple:
        """500服务器错误处理
        
        记录详细错误信息并返回友好的错误页面
        """
        # 记录完整错误信息（包含堆栈跟踪）
        log_request_details(app.logger, request, 'error', 
                           f"服务器内部错误: {str(error)}", 
                           exc_info=True)
        
        # 检查是否存在自定义500错误页面
        error_template_path = os.path.join(app.template_folder, '500.html')
        if os.path.exists(error_template_path):
            return render_template('500.html'), 500
        
        # 返回默认错误信息
        return '<h1>服务器内部错误，请稍后重试</h1>', 500


# ======================== 日志配置函数 ========================
def configure_logging(app: Flask) -> None:
    """
    配置应用日志系统
    
    针对不同环境优化日志格式和级别：
    - 开发环境：控制台详细日志，包含调试信息
    - 生产环境：文件日志（轮转）+ 控制台日志，更规范的格式
    """
    # 1. 配置werkzeug logger（禁用或自定义Flask的默认访问日志）
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.handlers.clear()  # 清除默认处理器
    
    # 生产环境完全禁用werkzeug默认日志，使用我们自己的日志系统
    if not app.debug and not app.testing:
        werkzeug_logger.setLevel(logging.CRITICAL)  # 只记录严重错误
    else:
        # 开发环境可以保留，但使用我们的格式
        werkzeug_handler = logging.StreamHandler()
        werkzeug_handler.setFormatter(logging.Formatter(
            '%(asctime)s [WERKZEUG] %(message)s'
        ))
        werkzeug_logger.addHandler(werkzeug_handler)
        werkzeug_logger.setLevel(logging.INFO)
    
    # 2. 清除应用日志现有处理器，避免重复
    app.logger.handlers.clear()
    
    # 2. 获取日志配置参数
    log_level: str = getattr(current_config, 'LOG_LEVEL', 'INFO')
    log_file: str = getattr(current_config, 'LOG_FILE', 'logs/app.log')
    log_max_bytes: int = getattr(current_config, 'LOG_MAX_BYTES', 1024 * 1024 * 5)  # 默认5MB
    log_backup_count: int = getattr(current_config, 'LOG_BACKUP_COUNT', 30)  # 默认保留30个备份
    
    # 3. 日志级别容错处理
    numeric_level: int = getattr(logging, log_level.upper(), logging.INFO)
    
    # 4. 开发/测试环境配置
    if app.debug or app.testing:
        # 增强的控制台日志格式 - 开发环境需要更多调试信息
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s [模块:%(module)s 函数:%(funcName)s 行:%(lineno)d]'
        ))
        console_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(console_handler)
        app.logger.setLevel(logging.DEBUG)
        
        app.logger.info("【开发环境】日志系统已配置完成 - 调试模式")
        return
    
    # 5. 生产环境配置
    try:
        # 5.1 创建日志目录
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # 5.2 文件日志处理器配置（按大小轮转）
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=log_max_bytes,
            backupCount=log_backup_count,
            encoding='utf-8'  # 强制UTF-8编码，确保中文正常显示
        )
        # 详细的文件日志格式 - 包含完整上下文信息
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)7s] [进程:%(process)d] [线程:%(threadName)s] ' \
            '[%(module)s:%(funcName)s:%(lineno)d] - %(message)s'
        ))
        file_handler.setLevel(numeric_level)
        
        # 5.3 控制台日志处理器配置（容器环境友好，日志级别可配置）
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s'
        ))
        console_handler.setLevel(numeric_level)
        
        # 5.4 注册日志处理器
        app.logger.addHandler(file_handler)
        app.logger.addHandler(console_handler)
        
        # 5.5 设置日志级别
        app.logger.setLevel(numeric_level)
        
        # 5.6 记录启动信息 - 更详细的环境信息
        app.logger.info(
            f"【系统启动】应用启动成功 | 环境：生产 | 日志级别：{log_level.upper()} "
            f"| 端口：{app.config.get('PORT', 5000)} | 主机：{app.config.get('HOST', '0.0.0.0')} "
            f"| 日志文件：{log_file} | 最大文件大小：{log_max_bytes/(1024*1024):.1f}MB "
            f"| 备份数量：{log_backup_count}"
        )
        
    except Exception as e:
        # 日志配置失败时，使用简单的控制台日志作为后备方案
        fallback_handler = logging.StreamHandler()
        fallback_handler.setFormatter(logging.Formatter(
            '%(asctime)s [ERROR] 日志配置失败: %(message)s'
        ))
        app.logger.addHandler(fallback_handler)
        app.logger.setLevel(logging.ERROR)
        app.logger.error(f"无法配置日志系统: {str(e)}")

# ======================== 应用实例创建 ========================
# 创建应用实例，根据环境变量自动选择配置
app = create_app(current_config)

# ======================== 应用启动入口 ========================
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',  # 允许所有网络接口访问
        port=app.config.get('PORT', 5000),  # 从配置读取端口
        debug=app.config.get('DEBUG', False)  # 调试模式（生产环境必须关闭）
    )