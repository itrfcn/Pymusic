import os
import re
import datetime
import json
from collections import Counter, defaultdict
from flask import Blueprint, jsonify, request, current_app
from apps.tool.Mysql import Mysql
# 导入管理员权限验证装饰器
from apps.admin import admin_required
from config import current_config

# 创建蓝图对象
analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

# 日志文件路径 - 从配置获取，确保与app.py一致
LOG_FILE_PATH = getattr(current_config, 'LOG_FILE', 'logs/app.log')

# 确保日志目录存在
log_dir = os.path.dirname(LOG_FILE_PATH)
if log_dir:
    os.makedirs(log_dir, exist_ok=True)


def analyze_user_growth(start_date=None, end_date=None):
    """
    分析用户增长数量
    
    Args:
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
    
    Returns:
        dict: 用户增长数据，按日期分组
    """
    try:
        with Mysql() as mysql:
            # 构建查询条件
            where_clause = ["deleted = 0"]
            params = []
            
            if start_date:
                where_clause.append("DATE(create_time) >= %s")
                params.append(start_date)
            if end_date:
                where_clause.append("DATE(create_time) <= %s")
                params.append(end_date)
            
            # 组合查询条件
            where_sql = "WHERE " + " AND ".join(where_clause)
            
            # 执行查询
            query = f"""
                SELECT DATE(create_time) as date, COUNT(*) as new_users
                FROM user
                {where_sql}
                GROUP BY DATE(create_time)
                ORDER BY date
            """
            result = mysql.sql(query, params)
            
            # 转换为字典格式
            user_growth = {}
            if result is not None:
                for item in result:
                    user_growth[str(item['date'])] = item['new_users']
            
            return user_growth
    except Exception as e:
        current_app.logger.error(f"分析用户增长数据失败: {str(e)}")
        return {}


def analyze_website_visits(start_date=None, end_date=None):
    """
    分析网站访问量
    
    Args:
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
    
    Returns:
        dict: 网站访问量数据
    """
    try:
        # 检查日志文件是否存在
        if not os.path.exists(LOG_FILE_PATH):
            current_app.logger.warning(f"日志文件不存在: {LOG_FILE_PATH}")
            # 创建空的日志文件，确保下次有日志写入
            with open(LOG_FILE_PATH, 'w', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]} [INFO] 日志文件已创建\n")
            return {"total_visits": 0, "daily_visits": {}}
        
        # 读取日志文件
        with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
            log_lines = f.readlines()
        
        # 日志格式正则表达式 - 适配实际日志格式
        log_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d{3} \[.*?\] \[.*?\] \[.*?\] \[.*?\] - .*')
        
        # 解析日志并统计访问量
        total_visits = 0
        daily_visits = defaultdict(int)
        
        for line in log_lines:
            match = log_pattern.match(line.strip())
            if match:
                log_date = match.group(1).split(' ')[0]  # 获取日期部分
                
                # 检查是否在日期范围内
                if start_date and log_date < start_date:
                    continue
                if end_date and log_date > end_date:
                    continue
                
                # 统计访问量
                total_visits += 1
                daily_visits[log_date] += 1
        
        return {
            "total_visits": total_visits,
            "daily_visits": dict(daily_visits)
        }
    except Exception as e:
        current_app.logger.error(f"分析网站访问量失败: {str(e)}")
        return {"total_visits": 0, "daily_visits": {}}


def analyze_visit_paths():
    """
    分析网站访问路径量
    
    Returns:
        dict: 访问路径数据，按路径分组
    """
    try:
        # 检查日志文件是否存在
        if not os.path.exists(LOG_FILE_PATH):
            current_app.logger.warning(f"日志文件不存在: {LOG_FILE_PATH}")
            # 创建空的日志文件，确保下次有日志写入
            with open(LOG_FILE_PATH, 'w', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]} [INFO] 日志文件已创建\n")
            return {}
        
        # 读取日志文件
        with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
            log_lines = f.readlines()
        
        # 日志路径正则表达式 - 适配实际日志格式，使用更通用的方法
        path_pattern = re.compile(r'\|.*?(/.*?) \|')
        
        # 统计访问路径
        path_counts = Counter()
        
        for line in log_lines:
            match = path_pattern.search(line.strip())
            if match:
                path = match.group(1)
                path_counts[path] += 1
        
        return dict(path_counts)
    except Exception as e:
        current_app.logger.error(f"分析访问路径失败: {str(e)}")
        return {}


def analyze_user_ip_locations():
    """
    分析网站用户IP所在地的数量
    
    Returns:
        dict: IP地址统计数据
    """
    try:
        # 检查日志文件是否存在
        if not os.path.exists(LOG_FILE_PATH):
            current_app.logger.warning(f"日志文件不存在: {LOG_FILE_PATH}")
            # 创建空的日志文件，确保下次有日志写入
            with open(LOG_FILE_PATH, 'w', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]} [INFO] 日志文件已创建\n")
            return {"total_ips": 0, "ip_counts": {}}
        
        # 读取日志文件
        with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
            log_lines = f.readlines()
        
        # IP地址正则表达式 - 适配实际日志格式
        ip_pattern = re.compile(r'IP: (.*?) \|')
        
        # 统计IP地址
        ip_counts = Counter()
        
        for line in log_lines:
            match = ip_pattern.search(line.strip())
            if match:
                ip = match.group(1)
                ip_counts[ip] += 1
        
        return {
            "total_ips": len(ip_counts),
            "ip_counts": dict(ip_counts)
        }
    except Exception as e:
        current_app.logger.error(f"分析用户IP位置失败: {str(e)}")
        return {"total_ips": 0, "ip_counts": {}}


@analytics_bp.route('/user-growth', methods=['GET'])
@admin_required
def get_user_growth():
    """
    获取用户增长数据接口
    
    Query Parameters:
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 验证日期格式
        if start_date:
            datetime.datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            datetime.datetime.strptime(end_date, '%Y-%m-%d')
        
        data = analyze_user_growth(start_date, end_date)
        
        return jsonify({
            "code": 200,
            "msg": "获取用户增长数据成功",
            "data": data
        })
    except ValueError as e:
        return jsonify({
            "code": 400,
            "msg": "日期格式错误，应为YYYY-MM-DD",
            "data": None
        }), 400
    except Exception as e:
        current_app.logger.error(f"获取用户增长数据接口错误: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": "系统错误，请稍后重试",
            "data": None
        }), 500


@analytics_bp.route('/website-visits', methods=['GET'])
@admin_required
def get_website_visits():
    """
    获取网站访问量数据接口
    
    Query Parameters:
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 验证日期格式
        if start_date:
            datetime.datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            datetime.datetime.strptime(end_date, '%Y-%m-%d')
        
        data = analyze_website_visits(start_date, end_date)
        
        return jsonify({
            "code": 200,
            "msg": "获取网站访问量数据成功",
            "data": data
        })
    except ValueError as e:
        return jsonify({
            "code": 400,
            "msg": "日期格式错误，应为YYYY-MM-DD",
            "data": None
        }), 400
    except Exception as e:
        current_app.logger.error(f"获取网站访问量数据接口错误: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": "系统错误，请稍后重试",
            "data": None
        }), 500


@analytics_bp.route('/visit-paths', methods=['GET'])
@admin_required
def get_visit_paths():
    """
    获取网站访问路径数据接口
    """
    try:
        data = analyze_visit_paths()
        
        return jsonify({
            "code": 200,
            "msg": "获取访问路径数据成功",
            "data": data
        })
    except Exception as e:
        current_app.logger.error(f"获取访问路径数据接口错误: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": "系统错误，请稍后重试",
            "data": None
        }), 500


@analytics_bp.route('/ip-locations', methods=['GET'])
@admin_required
def get_ip_locations():
    """
    获取用户IP位置数据接口
    """
    try:
        data = analyze_user_ip_locations()
        
        return jsonify({
            "code": 200,
            "msg": "获取IP位置数据成功",
            "data": data
        })
    except Exception as e:
        current_app.logger.error(f"获取IP位置数据接口错误: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": "系统错误，请稍后重试",
            "data": None
        }), 500


@analytics_bp.route('/dashboard', methods=['GET'])
@admin_required
def get_dashboard_data():
    """
    获取仪表盘综合数据接口
    """
    try:
        # 获取当前日期和一周前的日期
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
        
        # 并行获取所有数据
        user_growth = analyze_user_growth(start_date, end_date)
        website_visits = analyze_website_visits(start_date, end_date)
        visit_paths = analyze_visit_paths()
        ip_locations = analyze_user_ip_locations()
        
        # 计算总用户数
        with Mysql() as mysql:
            result = mysql.sql("SELECT COUNT(*) as count FROM user WHERE deleted = 0")
            total_users = result[0]['count'] if result is not None and result else 0
        
        data = {
            "total_users": total_users,
            "total_visits": website_visits.get("total_visits", 0),
            "total_ips": ip_locations.get("total_ips", 0),
            "user_growth": user_growth,
            "daily_visits": website_visits.get("daily_visits", {}),
            "top_paths": dict(sorted(visit_paths.items(), key=lambda x: x[1], reverse=True)[:10]),
            "top_ips": dict(sorted(ip_locations.get("ip_counts", {}).items(), key=lambda x: x[1], reverse=True)[:10])
        }
        
        return jsonify({
            "code": 200,
            "msg": "获取仪表盘数据成功",
            "data": data
        })
    except Exception as e:
        current_app.logger.error(f"获取仪表盘数据接口错误: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": "系统错误，请稍后重试",
            "data": None
        }), 500
