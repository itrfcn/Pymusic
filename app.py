import os
import re
import logging
import time
from typing import List, Dict, Tuple
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template, request, session, redirect, abort
from werkzeug.middleware.proxy_fix import ProxyFix

# 导入项目依赖
from config import current_config
from apps.music import music  # 音乐模块蓝图
from apps.user import user  # 用户模块蓝图
from apps.clean_history_data import register_cleanup_hook  # 历史数据清理钩子


# ======================== 防护扫描机制 ========================

# IP访问频率限制存储
ip_requests: Dict[str, List[float]] = {}
# 恶意请求记录
malicious_requests: Dict[str, int] = {}


def is_ip_whitelisted(ip: str) -> bool:
    """检查IP是否在白名单中
    
    Args:
        ip: 客户端IP地址
    
    Returns:
        bool: 是否在白名单中
    """
    return ip in current_config.IP_WHITELIST


def is_ip_blacklisted(ip: str) -> bool:
    """检查IP是否在黑名单中
    
    Args:
        ip: 客户端IP地址
    
    Returns:
        bool: 是否在黑名单中
    """
    return ip in current_config.IP_BLACKLIST


def check_ip_rate_limit(ip: str) -> Tuple[bool, int]:
    """检查IP访问频率限制
    
    Args:
        ip: 客户端IP地址
    
    Returns:
        Tuple[bool, int]: (是否通过限制, 剩余请求数)
    """
    if not current_config.IP_RATE_LIMIT_ENABLED:
        return True, current_config.IP_RATE_LIMIT
    
    current_time = time.time()
    # 清理过期的请求记录
    if ip in ip_requests:
        ip_requests[ip] = [t for t in ip_requests[ip] if current_time - t < current_config.IP_RATE_LIMIT_WINDOW]
    else:
        ip_requests[ip] = []
    
    # 检查请求数是否超过限制
    if len(ip_requests[ip]) >= current_config.IP_RATE_LIMIT:
        return False, 0
    
    # 记录当前请求时间
    ip_requests[ip].append(current_time)
    remaining = current_config.IP_RATE_LIMIT - len(ip_requests[ip])
    return True, remaining


def detect_sql_injection(content: str) -> bool:
    """检测SQL注入攻击
    
    Args:
        content: 要检测的内容
    
    Returns:
        bool: 是否包含SQL注入模式
    """
    for pattern in current_config.SQL_INJECTION_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    return False


def detect_xss(content: str) -> bool:
    """检测XSS攻击
    
    Args:
        content: 要检测的内容
    
    Returns:
        bool: 是否包含XSS模式
    """
    for pattern in current_config.XSS_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    return False


def detect_abnormal_ua(ua: str) -> bool:
    """检测异常User-Agent
    
    Args:
        ua: User-Agent字符串
    
    Returns:
        bool: 是否为异常User-Agent
    """
    for pattern in current_config.ABNORMAL_UA_PATTERNS:
        if re.search(pattern, ua, re.IGNORECASE):
            return True
    return False


def block_scan_ua(ua: str) -> bool:
    """拦截特定扫描User-Agent
    
    Args:
        ua: User-Agent字符串
    
    Returns:
        bool: 是否为需要拦截的扫描User-Agent
    """
    if not ua:
        return False
    
    block_keywords = current_config.BLOCK_UA_KEYWORDS
    for keyword in block_keywords:
        if keyword.strip().lower() in ua.lower():
            return True
    return False


def check_malicious_request(request_data: str) -> Tuple[bool, str]:
    """检查恶意请求
    
    Args:
        request_data: 请求数据
    
    Returns:
        Tuple[bool, str]: (是否为恶意请求, 检测到的攻击类型)
    """
    # 恶意请求检测逻辑
    # 注：cover_url字段已在收集请求数据时被移除，避免Base64被误判
    
    if detect_sql_injection(request_data):
        return True, "SQL注入攻击"
    if detect_xss(request_data):
        return True, "XSS攻击"
    return False, ""


# ======================== 日志辅助函数 ========================
def get_real_ip(request):
    """获取真实的客户端IP地址，支持反向代理环境
    
    优先检查常见的反向代理头，最后回退到remote_addr
    
    Args:
        request: Flask请求对象
    
    Returns:
        str: 真实的IP地址
    """
    # 宝塔面板等反向代理常用的头
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    
    # 标准的X-Forwarded-For头（可能包含多个IP，取第一个）
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        # X-Forwarded-For可能包含多个代理IP，取第一个非空值
        ips = [ip.strip() for ip in x_forwarded_for.split(',') if ip.strip()]
        if ips:
            return ips[0]
    
    # 回退到原始的remote_addr
    return request.remote_addr

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
        'IP': get_real_ip(request),
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
    
    # 配置ProxyFix中间件，支持反向代理环境下获取真实IP
    # x_for=1: 信任第一个X-Forwarded-For头
    # x_proto=1: 信任X-Forwarded-Proto头
    # x_host=1: 信任X-Forwarded-Host头
    # x_prefix=1: 信任X-Forwarded-Prefix头
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
        x_prefix=1
    )
    
    # 配置在反向代理环境下正确处理请求头
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    
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
    
    # 5. 添加全局防护扫描中间件
    try:
        @app.before_request
        def global_protection_scan():
            """全局防护扫描中间件
            
            拦截所有请求并进行安全检查
            """
            # 获取客户端真实IP
            client_ip = get_real_ip(request)
            user_agent = request.headers.get('User-Agent', '未知')
            
            # 1. IP白名单检查
            if is_ip_whitelisted(client_ip):
                app.logger.info(f"IP白名单允许访问: {client_ip}")
                return None
            
            # 2. IP黑名单检查
            if is_ip_blacklisted(client_ip):
                app.logger.warning(f"IP黑名单拒绝访问: {client_ip}")
                abort(403, description="IP地址被禁止访问")
            
            # 3. IP访问频率限制
            rate_limit_passed, remaining = check_ip_rate_limit(client_ip)
            if not rate_limit_passed:
                app.logger.warning(f"IP访问频率限制: {client_ip} | 超过限制")
                abort(429, description="请求过于频繁，请稍后再试")
            
            # 4. 异常User-Agent检测
            if detect_abnormal_ua(user_agent):
                app.logger.warning(f"异常User-Agent检测: {client_ip} | UA: {user_agent}")
                # 可以选择记录日志或者直接拒绝访问
                # abort(403, description="不允许的访问方式")
            
            # 5. 拦截特定扫描User-Agent
            if block_scan_ua(user_agent):
                app.logger.warning(f"扫描User-Agent拦截: {client_ip} | UA: {user_agent}")
                abort(403, description="不允许的访问方式")
            
            # 5. 恶意请求检测
            if current_config.MALICIOUS_REQUEST_DETECTION:
                # 收集请求数据进行检测
                request_data = ""
                
                # 检查URL参数
                if request.args:
                    request_data += str(request.args)
                
                # 检查表单数据
                if request.form:
                    request_data += str(request.form)
                
                # 检查JSON数据
                try:
                    if request.is_json:
                        json_data = request.get_json()
                        # 特殊处理：移除cover_url字段以避免Base64被误判
                        if isinstance(json_data, dict) and 'cover_url' in json_data:
                            json_data_copy = json_data.copy()
                            del json_data_copy['cover_url']
                            request_data += str(json_data_copy)
                        else:
                            request_data += str(json_data)
                except Exception:
                    pass
                
                # 检查请求头中的可疑字段
                suspicious_headers = ['Referer', 'X-Forwarded-For', 'X-Real-IP']
                for header in suspicious_headers:
                    if header in request.headers:
                        request_data += request.headers[header]
                
                # 检测恶意请求
                is_malicious, attack_type = check_malicious_request(request_data)
                if is_malicious:
                    # 记录恶意请求
                    if client_ip in malicious_requests:
                        malicious_requests[client_ip] += 1
                    else:
                        malicious_requests[client_ip] = 1
                    
                    app.logger.warning(f"恶意请求检测: {client_ip} | 攻击类型: {attack_type} | 数据: {request_data[:200]}...")
                    
                    # 多次恶意请求可考虑加入黑名单
                    if malicious_requests[client_ip] >= 5:
                        app.logger.critical(f"IP多次恶意请求，建议加入黑名单: {client_ip} | 次数: {malicious_requests[client_ip]}")
                    
                    abort(403, description="请求包含恶意内容")
            
            # 6. 记录请求信息（可选）
            app.logger.info(f"防护扫描通过: {client_ip} | 剩余请求: {remaining} | UA: {user_agent}")
            
        app.logger.info("全局防护扫描中间件注册完成")
    except Exception as e:
        app.logger.error("全局防护扫描中间件注册失败", exc_info=True)
        raise

    # 6. 定义核心路由
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
        # 校验页面名称是否包含非法字符
        if not PARTIAL_CHAR_PATTERN.match(page_name):
            log_request_details(app.logger, request, 'warning', 
                               f"非法页面请求: {page_name}， 可能的路径注入尝试")
            abort(404)
        # 登录注册页面路由
        if page_name == 'login':
            log_request_details(app.logger, request, 'info', f"用户访问登录页面")
            return render_template('user/login.html')
        if page_name == 'register':
            log_request_details(app.logger, request, 'info', f"用户访问注册页面")
            return render_template('user/register.html')

        # 无效页面兜底处理，有利于搜索引擎收录
        if page_name not in ALLOWED_PAGES:
            log_request_details(app.logger, request, 'warning', 
                               f"无效页面请求: {page_name}，已重定向至默认页面")
            page_name = 'discover'
        
        # 权限校验：未登录用户无法访问受保护页面
        if page_name in PROTECTED_PAGES and 'user_id' not in session:
            log_request_details(app.logger, request, 'info', 
                               f"未登录用户尝试访问受保护页面: {page_name}，已重定向至登录页")
            return redirect(url_for('index', page_name='login'))
        
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
        
        详细记录404错误信息并返回自定义404页面
        """
        # 记录详细404错误信息
        log_request_details(app.logger, request, 'warning', 
                           f"页面404: {request.path}")
        return render_template('404.html'), 404
    
    @app.errorhandler(403)
    def forbidden(error) -> tuple:
        """403禁止访问错误处理
        
        记录详细错误信息并返回自定义403页面
        """
        # 记录详细403错误信息
        log_request_details(app.logger, request, 'warning', 
                           f"禁止访问: {request.path} | 原因: {str(error.description) if hasattr(error, 'description') else '未知原因'}")
        return '<h1>禁止访问</h1>', 403


    @app.errorhandler(429)
    def too_many_requests(error) -> tuple:
        """429请求频率限制错误处理
        
        记录详细错误信息并返回自定义429页面
        """
        # 记录详细429错误信息
        log_request_details(app.logger, request, 'warning', 
                           f"请求过于频繁: {request.path}")
        return '<h1>请求过于频繁，请稍后再试</h1>', 429
    
    @app.errorhandler(405)
    def method_not_allowed(error) -> tuple:
        """405方法不允许错误处理
        
        记录详细错误信息并返回自定义405页面
        """
        # 记录详细405错误信息
        log_request_details(app.logger, request, 'warning', 
                           f"方法不允许: {request.path}")
        return '<h1>方法不允许</h1>', 405
    
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
        host=app.config.get('HOST', '0.0.0.0'),  # 允许所有网络接口访问
        port=app.config.get('PORT', 5000),  # 从配置读取端口
        debug=app.config.get('DEBUG', False)  # 调试模式（生产环境必须关闭）
    )