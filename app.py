import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template, request, session, redirect, url_for
from config import current_config
# 导入蓝图
from apps.music import music
from apps.user import user
# 导入清理历史数据的钩子
from apps.clean_history_data import register_cleanup_hook

#工厂函数，用于创建Flask应用实例
def create_app(config_name=None):
    """创建Flask应用实例"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config_name)
    
    # 配置日志
    configure_logging(app)
    
    # 注册蓝图
    app.register_blueprint(music)
    app.register_blueprint(user)
    
    # 注册播放历史清理钩子
    register_cleanup_hook(app)

    # 全局请求钩子，检查登录状态
    @app.before_request
    def check_login():
        # 允许访问的路径（无需登录）
        allowed_paths = ['/','/user/login', '/user/register', '/static/']

        # 检查当前请求路径是否需要登录验证
        need_login = True
        for path in allowed_paths:
            if request.path.startswith(path):
                need_login = False
                break

        # 如果需要登录但没有 session，则重定向到登录页面
        if need_login and 'user_id' not in session:
            return redirect(url_for('user.login'))

    @app.route('/')
    @app.route('/<page_name>')
    def index(page_name='discover'):
        if page_name not in ['discover', 'rank', 'doc-163', 'about']:
            page_name = 'discover'
        return render_template('index.html', page=page_name)


    @app.route('/playlist/<int:playlist_id>')
    def playlist_detail(playlist_id):
        # 首页路由，前端会通过AJAX请求获取歌单详情数据
        return render_template('index.html', page='playlist_detail', playlist_id=playlist_id)

    @app.route('/partials/playlist_detail')
    def playlist_detail_partial():
        # 提供歌单详情的部分视图，用于AJAX加载
        return render_template('partials/playlist_detail.html')


    @app.route('/partials/<page_name>')
    def partial(page_name):
        # 检查模板文件是否存在
        template_path = f'{app.template_folder}/partials/{page_name}.html'
        if not os.path.exists(template_path):
            # 文件不存在时返回404页面
            return render_template('404.html'), 404
        return render_template(f'partials/{page_name}.html')

    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404


    return app

# 配置应用日志
def configure_logging(app):
    """配置应用日志"""
    # 如果是调试模式，不配置文件日志
    if app.debug or app.testing:
        return
    
    # 创建日志目录
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # 设置日志级别
    log_level = getattr(current_config, 'LOG_LEVEL', 'INFO')
    numeric_level = getattr(logging, log_level.upper(), None)
    
    # 配置RotatingFileHandler
    file_handler = RotatingFileHandler(
        getattr(current_config, 'LOG_FILE', 'logs/app.log'),
        maxBytes=10240,  # 10KB
        backupCount=10   # 保留10个备份
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(numeric_level)
    app.logger.addHandler(file_handler)
    
    # 设置根日志级别
    app.logger.setLevel(numeric_level)
    app.logger.info('应用启动')


app = create_app(current_config)
if __name__ == '__main__':
    # 关键添加：host='0.0.0.0'（允许外部访问），port可自定义（默认5000）
    app.run(
        host='0.0.0.0',  # 核心修改：允许所有外部IP连接
        port=5000,       # 端口可按需修改（如5001、8080）
        debug=True  # 生产环境必须设置为False，提高安全性
    )