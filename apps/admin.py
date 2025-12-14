from flask import Blueprint, request, jsonify, current_app, session
from werkzeug.security import check_password_hash
from functools import wraps
from apps.tool.Mysql import Mysql
import hashlib

# 创建admin蓝图
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# 管理员权限装饰器
def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # 检查是否登录
        if 'user_id' not in session:
            return jsonify({
                'code': 401,
                'msg': '请先登录',
                'data': None
            }), 401
            
        # 检查是否为管理员
        user_id = session.get('user_id')
        with Mysql() as mysql:
            user = mysql.sql(f"SELECT is_admin FROM user WHERE id = {user_id} AND deleted = 0")
            if not user or not user[0]['is_admin']:
                return jsonify({
                    'code': 403,
                    'msg': '没有管理员权限',
                    'data': None
                }), 403
                
        return func(*args, **kwargs)
    return decorated_function


# 管理员登录接口
@admin_bp.route('/login', methods=['POST'])
def admin_login():
    """
    管理员登录接口
    """
    try:
        # 获取登录参数
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.form.get('username')
            password = request.form.get('password')
        
        # 参数验证
        if not username or not password:
            return jsonify({'code': 400, 'msg': '请提供用户名和密码', 'data': None}), 400
            
        # 查询用户信息
        with Mysql() as mysql:
            user = mysql.sql(f"SELECT id, username, password, status, is_admin FROM user WHERE username='{username}' AND deleted = 0")
            
            # 用户不存在或密码错误
            if not user:
                return jsonify({'code': 401, 'msg': '用户名或密码错误', 'data': None}), 401
                
            user = user[0]
            
            # 检查用户状态
            if user['status'] != 0:
                return jsonify({'code': 403, 'msg': '账号已禁用', 'data': None}), 403
                
            # 检查是否为管理员
            if not user['is_admin']:
                return jsonify({'code': 403, 'msg': '没有管理员权限', 'data': None}), 403
                
            # 验证密码
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if user['password'] != hashed_password:
                return jsonify({'message': '用户名或密码错误'}), 401
                
            # 设置session
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = True
            
            # 记录日志
            current_app.logger.info(f"管理员登录成功: {username}")
            
            return jsonify({
                'code': 200,
                'msg': '登录成功',
                'data': {
                    'user_id': user['id'],
                    'username': user['username'],
                    'is_admin': user['is_admin']
                }
            }), 200
            
    except Exception as e:
        current_app.logger.error(f"管理员登录错误: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '系统错误，请稍后重试',
            'data': None
        }), 500


# 管理员接口：获取所有用户列表
@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    """
    管理员获取所有用户列表
    """
    try:
        with Mysql() as mysql:
            select_sql = "SELECT id, username, netease_user_id, status, is_admin, create_time FROM user WHERE deleted = 0"
            users = mysql.sql(select_sql)
            return jsonify({
                'code': 200,
                'msg': '获取用户列表成功',
                'data': users
            }), 200
    except Exception as e:
        current_app.logger.error(f"获取用户列表错误: {str(e)}")
        return jsonify({'message': '系统错误，请稍后重试'}), 500


# 管理员接口：删除用户
@admin_bp.route('/users/<int:target_user_id>', methods=['DELETE'])
@admin_required
def delete_user(target_user_id):
    """
    管理员删除用户
    """
    try:
        # 防止删除自己
        current_user_id = session.get('user_id')
        if current_user_id == target_user_id:
            return jsonify({
                'code': 400,
                'msg': '不能删除自己',
                'data': None
            }), 400
            
        with Mysql() as mysql:
            # 检查用户是否存在
            select_sql = f"SELECT id FROM user WHERE id = {target_user_id} AND deleted = 0"
            user = mysql.sql(select_sql)
            if not user:
                return jsonify({
                'code': 404,
                'msg': '用户不存在',
                'data': None
            }), 404
            
            # 逻辑删除用户
            delete_sql = f"UPDATE user SET deleted = 1 WHERE id = {target_user_id}"
            result = mysql.sql(delete_sql)
            
            # 删除用户的所有歌单
            delete_playlists_sql = f"UPDATE playlist SET deleted = 1 WHERE user_id = {target_user_id}"
            mysql.sql(delete_playlists_sql)
            
            return jsonify({
                'code': 200,
                'msg': '删除用户成功',
                'data': None
            }), 200
    except Exception as e:
        current_app.logger.error(f"删除用户错误: {str(e)}")
        return jsonify({'code': 500, 'msg': '系统错误，请稍后重试', 'data': None}), 500


# 管理员接口：封禁用户
@admin_bp.route('/users/<int:target_user_id>/ban', methods=['PUT'])
@admin_required
def ban_user(target_user_id):
    """
    管理员封禁用户
    """
    try:
        # 防止封禁自己
        current_user_id = session.get('user_id')
        if current_user_id == target_user_id:
            return jsonify({
                'code': 400,
                'msg': '不能封禁自己',
                'data': None
            }), 400
            
        with Mysql() as mysql:
            # 检查用户是否存在
            select_sql = f"SELECT id FROM user WHERE id = {target_user_id} AND deleted = 0"
            user = mysql.sql(select_sql)
            if not user:
                return jsonify({'code': 404, 'msg': '用户不存在', 'data': None}), 404
            
            # 封禁用户
            ban_sql = f"UPDATE user SET status = 0 WHERE id = {target_user_id}"
            result = mysql.sql(ban_sql)
            
            return jsonify({
                'code': 200,
                'msg': '封禁用户成功',
                'data': None
            }), 200
    except Exception as e:
        current_app.logger.error(f"封禁用户错误: {str(e)}")
        return jsonify({'code': 500, 'msg': '系统错误，请稍后重试', 'data': None}), 500


# 管理员接口：解放用户
@admin_bp.route('/users/<int:target_user_id>/unban', methods=['PUT'])
@admin_required
def unban_user(target_user_id):
    """
    管理员解放用户
    """
    try:
        with Mysql() as mysql:
            # 检查用户是否存在
            select_sql = f"SELECT id FROM user WHERE id = {target_user_id} AND deleted = 0"
            user = mysql.sql(select_sql)
            if not user:
                return jsonify({'code': 404, 'msg': '用户不存在', 'data': None}), 404
            
            # 解放用户
            unban_sql = f"UPDATE user SET status = 1 WHERE id = {target_user_id}"
            result = mysql.sql(unban_sql)
            
            return jsonify({
                'code': 200,
                'msg': '解放用户成功',
                'data': None
            }), 200
    except Exception as e:
        current_app.logger.error(f"解放用户错误: {str(e)}")
        return jsonify({'code': 500, 'msg': '系统错误，请稍后重试', 'data': None}), 500


# 管理员接口：设置用户为管理员
@admin_bp.route('/users/<int:target_user_id>/set_admin', methods=['PUT'])
@admin_required
def set_user_admin(target_user_id):
    """
    管理员设置用户为管理员
    """
    try:
        with Mysql() as mysql:
            # 检查用户是否存在
            select_sql = f"SELECT id FROM user WHERE id = {target_user_id} AND deleted = 0"
            user = mysql.sql(select_sql)
            if not user:
                return jsonify({'code': 404, 'msg': '用户不存在', 'data': None}), 404
            
            # 设置为管理员
            set_admin_sql = f"UPDATE user SET is_admin = 1 WHERE id = {target_user_id}"
            result = mysql.sql(set_admin_sql)
            
            return jsonify({
                'code': 200,
                'msg': '设置用户为管理员成功',
                'data': None
            }), 200
    except Exception as e:
        current_app.logger.error(f"设置用户为管理员错误: {str(e)}")
        return jsonify({'code': 500, 'msg': '系统错误，请稍后重试', 'data': None}), 500


# 管理员接口：修改用户信息
@admin_bp.route('/users/<int:target_user_id>', methods=['PUT'])
@admin_required
def update_user_info(target_user_id):
    """
    管理员修改用户信息（用户名、密码、网易云ID）
    """
    try:
        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')
        netease_user_id = data.get('netease_user_id')
        
        # 检查至少提供了一个需要修改的字段
        if not any([username, password, netease_user_id]):
            return jsonify({
            'code': 400,
            'msg': '请至少提供一个需要修改的字段',
            'data': None
        }), 400
        
        with Mysql() as mysql:
            # 检查用户是否存在
            user = mysql.sql(f"SELECT id, username FROM user WHERE id = {target_user_id} AND deleted = 0")
            if not user:
                return jsonify({'code': 404, 'msg': '用户不存在', 'data': None}), 404
            
            # 构建更新语句
            update_fields = []
            update_values = []
            
            if username:
                username = username.strip()
                if not username:
                    return jsonify({
                        'code': 400,
                        'msg': '用户名不能为空',
                        'data': None
                    }), 400
                    
                # 检查用户名是否已存在
                existing_user = mysql.sql(
                    "SELECT id FROM user WHERE username=%s AND deleted=0 AND status=0 AND id!=%s",
                    [username, target_user_id]
                )
                if existing_user:
                    return jsonify({
                        'code': 400,
                        'msg': '用户名已存在',
                        'data': None
                    }), 400
                    
                update_fields.append("username = %s")
                update_values.append(username)
            
            if password:
                password = password.strip()
                if not password:
                    return jsonify({
                        'code': 400,
                        'msg': '密码不能为空',
                        'data': None
                    }), 400
                    
                # 对密码进行哈希处理
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                update_fields.append("password = %s")
                update_values.append(hashed_password)
            
            if netease_user_id is not None:
                if netease_user_id == "":
                    # 允许清空网易云ID
                    update_fields.append("netease_user_id = NULL")
                else:
                    update_fields.append("netease_user_id = %s")
                    update_values.append(netease_user_id)
            
            if update_fields:
                # 添加更新时间
                update_fields.append("update_time = CURRENT_TIMESTAMP")
                
                # 构建完整的更新SQL
                update_sql = "UPDATE user SET " + ", ".join(update_fields) + " WHERE id = %s"
                update_values.append(target_user_id)
                
                # 执行更新
                mysql.sql(update_sql, update_values)
                
                current_app.logger.info(f"管理员修改用户信息成功: 用户ID {target_user_id}")
                return jsonify({
                    'code': 200,
                    'msg': '修改用户信息成功',
                    'data': None
                }), 200
            else:
                return jsonify({
                    'code': 400,
                    'msg': '没有可更新的字段',
                    'data': None
                }), 400
                
    except Exception as e:
        current_app.logger.error(f"管理员修改用户信息错误: {str(e)}")
        return jsonify({'code': 500, 'msg': '系统错误，请稍后重试', 'data': None}), 500


# 管理员接口：获取所有歌单
@admin_bp.route('/playlists', methods=['GET'])
@admin_required
def get_all_playlists():
    """
    管理员获取所有歌单
    """
    try:
        with Mysql() as mysql:
            # 查询所有未被删除的歌单，包含创建者用户名
            playlists = mysql.sql(
                '''SELECT p.id, p.user_id, u.username, p.name, p.cover_url, p.description, p.create_time, p.update_time,
                       COUNT(ps.song_id) as song_count
                FROM playlist p
                LEFT JOIN user u ON p.user_id = u.id
                LEFT JOIN playlist_song ps ON p.id = ps.playlist_id
                WHERE p.deleted=0
                GROUP BY p.id
                ORDER BY p.create_time DESC'''
            )
            
            current_app.logger.info(f"管理员获取所有歌单成功，共 {len(playlists)} 个歌单")
            return jsonify({
                'code': 200,
                'msg': '获取所有歌单成功',
                'data': {
                    'playlists': playlists,
                    'total': len(playlists)
                }
            }), 200
            
    except Exception as e:
        current_app.logger.error(f"管理员获取所有歌单错误: {str(e)}")
        return jsonify({'code': 500, 'msg': '系统错误，请稍后重试', 'data': None}), 500


# 管理员接口：根据用户ID获取歌单
@admin_bp.route('/users/<int:user_id>/playlists', methods=['GET'])
@admin_required
def get_user_playlists(user_id):
    """
    管理员根据用户ID获取歌单
    """
    try:
        with Mysql() as mysql:
            # 检查用户是否存在
            user = mysql.sql(f"SELECT id, username FROM user WHERE id = {user_id} AND deleted = 0")
            if not user:
                return jsonify({'code': 404, 'msg': '用户不存在', 'data': None}), 404
            
            # 查询该用户的所有未被删除的歌单
            playlists = mysql.sql(
                '''SELECT p.id, p.user_id, u.username, p.name, p.cover_url, p.description, p.create_time, p.update_time,
                       COUNT(ps.song_id) as song_count
                FROM playlist p
                LEFT JOIN user u ON p.user_id = u.id
                LEFT JOIN playlist_song ps ON p.id = ps.playlist_id
                WHERE p.user_id = %s AND p.deleted=0
                GROUP BY p.id
                ORDER BY p.create_time DESC''',
                [user_id]
            )
            
            current_app.logger.info(f"管理员获取用户 {user_id} 的歌单成功，共 {len(playlists)} 个歌单")
            return jsonify({
                'code': 200,
                'msg': '获取用户歌单成功',
                'data': {
                    'user': user[0],
                    'playlists': playlists,
                    'total': len(playlists)
                }
            }), 200
            
    except Exception as e:
        current_app.logger.error(f"管理员获取用户歌单错误: {str(e)}")
        return jsonify({'code': 500, 'msg': '系统错误，请稍后重试', 'data': None}), 500


# 管理员接口：单独修改某一用户的信息
@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_single_user(user_id):
    """
    管理员单独修改某一用户的信息，不必同时修改多个字段
    """
    try:
        with Mysql() as mysql:
            # 检查用户是否存在
            user = mysql.sql(
                "SELECT id, username FROM user WHERE id = %s AND deleted = 0",
                [user_id]
            )
            
            if not user:
                return jsonify({'code': 404, 'msg': '用户不存在', 'data': None}), 404
            
            # 获取请求数据
            data = request.get_json()
            if not data:
                return jsonify({
                'code': 400,
                'msg': '没有提供要修改的字段',
                'data': None
            }), 400
            
            # 允许修改的字段列表
            allowed_fields = ['username', 'status', 'is_admin']
            update_fields = []
            update_values = []
            
            # 构建更新语句
            for field, value in data.items():
                if field in allowed_fields:
                    # 特殊处理is_admin字段，确保它是整数0或1
                    if field == 'is_admin':
                        if value not in [0, 1]:
                            return jsonify({
                        'code': 400,
                        'msg': 'is_admin字段必须是0或1',
                        'data': None
                    }), 400
                        update_fields.append(f"{field} = %s")
                        update_values.append(value)
                    # 特殊处理status字段，确保它是整数0或1
                    elif field == 'status':
                        if value not in [0, 1]:
                            return jsonify({
                        'code': 400,
                        'msg': 'status字段必须是0或1',
                        'data': None
                    }), 400
                        update_fields.append(f"{field} = %s")
                        update_values.append(value)
                    # 处理username字段，确保不为空
                    elif field == 'username':
                        if not value or len(value.strip()) == 0:
                            return jsonify({
                            'code': 400,
                            'msg': '用户名不能为空',
                            'data': None
                        }), 400
                        # 检查新用户名是否已存在
                        existing_user = mysql.sql(
                            "SELECT id FROM user WHERE username = %s AND id != %s AND deleted = 0",
                            [value.strip(), user_id]
                        )
                        if existing_user:
                            return jsonify({
                            'code': 400,
                            'msg': '用户名已存在',
                            'data': None
                        }), 400
                        update_fields.append(f"{field} = %s")
                        update_values.append(value.strip())
            
            if not update_fields:
                return jsonify({
                'code': 400,
                'msg': '没有提供有效的字段进行修改',
                'data': None
            }), 400
            
            # 添加用户ID到更新值列表
            update_values.append(user_id)
            
            # 执行更新
            update_query = f"UPDATE user SET {', '.join(update_fields)} WHERE id = %s AND deleted = 0"
            mysql.sql(update_query, update_values)
            
            # 获取更新后的用户信息
            updated_user = mysql.sql(
                '''SELECT id, username, netease_user_id, status, is_admin, create_time, update_time 
                 FROM user WHERE id = %s AND deleted = 0''',
                [user_id]
            )
            
            current_app.logger.info(f"管理员更新用户 {user_id} 的信息成功，修改字段: {', '.join(allowed_fields)}")
            return jsonify({
                'code': 200,
                'msg': '更新用户信息成功',
                'data': updated_user[0]
            }), 200
            
    except Exception as e:
        current_app.logger.error(f"管理员更新用户信息错误: {str(e)}")
        return jsonify({'code': 500, 'msg': '系统错误，请稍后重试', 'data': None}), 500


# 管理员接口：获取单个用户的信息
@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_single_user(user_id):
    """
    管理员获取单个用户的详细信息
    """
    try:
        with Mysql() as mysql:
            # 查询用户详细信息
            user = mysql.sql(
                '''SELECT id, username, netease_user_id, status, is_admin, create_time, update_time 
                 FROM user WHERE id = %s AND deleted = 0''',
                [user_id]
            )
            
            if not user:
                return jsonify({'message': '用户不存在'}), 404
            
            current_app.logger.info(f"管理员获取用户 {user_id} 的详细信息成功")
            return jsonify({
                'code': 200,
                'msg': '获取用户信息成功',
                'data': user[0]
            }), 200
            
    except Exception as e:
        current_app.logger.error(f"管理员获取单个用户信息错误: {str(e)}")
        return jsonify({'code': 500, 'msg': '系统错误，请稍后重试', 'data': None}), 500


# 管理员接口：删除歌单
@admin_bp.route('/playlists/<int:playlist_id>', methods=['DELETE'])
@admin_required
def delete_playlist(playlist_id):
    """
    管理员删除歌单
    """
    try:
        with Mysql() as mysql:
            # 检查歌单是否存在
            playlist = mysql.sql(
                "SELECT id, user_id FROM playlist WHERE id = %s AND deleted = 0",
                [playlist_id]
            )
            
            if not playlist:
                return jsonify({
                'code': 404,
                'msg': '歌单不存在',
                'data': None
            }), 404
            
            # 逻辑删除歌单
            mysql.sql(
                "UPDATE playlist SET deleted = 1 WHERE id = %s",
                [playlist_id]
            )
            
            # 删除歌单中的所有歌曲关联
            mysql.sql(
                "DELETE FROM playlist_song WHERE playlist_id = %s",
                [playlist_id]
            )
            
            current_app.logger.info(f"管理员删除歌单 {playlist_id} 成功")
            return jsonify({
                'code': 200,
                'msg': '删除歌单成功',
                'data': None
            }), 200
            
    except Exception as e:
        current_app.logger.error(f"管理员删除歌单错误: {str(e)}")
        return jsonify({'code': 500, 'msg': '系统错误，请稍后重试', 'data': None}), 500


# 管理员接口：退出登录
@admin_bp.route('/logout', methods=['POST'])
def admin_logout():
    """
    管理员退出登录接口
    """
    try:
        # 记录退出登录的管理员信息
        if 'username' in session:
            username = session['username']
            current_app.logger.info(f"管理员退出登录: {username}")
        
        # 清除session中的所有信息
        session.clear()
        
        return jsonify({
            'code': 200,
            'msg': '退出登录成功',
            'data': None
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"管理员退出登录错误: {str(e)}")
        return jsonify({'code': 500, 'msg': '系统错误，请稍后重试', 'data': None}), 500


# 管理员接口：解除管理员权限
@admin_bp.route('/users/<int:user_id>/remove-admin', methods=['POST'])
@admin_required
def remove_admin(user_id):
    """
    管理员解除指定用户的管理员权限
    """
    try:
        with Mysql() as mysql:
            # 检查用户是否存在
            user = mysql.sql(
                "SELECT id, username, is_admin FROM user WHERE id = %s AND deleted = 0",
                [user_id]
            )
            
            if not user:
                return jsonify({'message': '用户不存在'}), 404
            
            # 检查用户是否是管理员
            if user[0]['is_admin'] != 1:
                return jsonify({
                'code': 400,
                'msg': '该用户不是管理员',
                'data': None
            }), 400
            
            # 检查是否是最后一个管理员
            admin_count = mysql.sql("SELECT COUNT(*) as count FROM user WHERE is_admin = 1 AND deleted = 0")[0]['count']
            if admin_count <= 1:
                return jsonify({
                'code': 400,
                'msg': '不能解除最后一个管理员的权限',
                'data': None
            }), 400
            
            # 解除管理员权限
            mysql.sql(
                "UPDATE user SET is_admin = 0 WHERE id = %s AND deleted = 0",
                [user_id]
            )
            
            current_app.logger.info(f"管理员解除用户 {user_id} 的管理员权限成功")
            return jsonify({
                'code': 200,
                'msg': '解除管理员权限成功',
                'data': None
            }), 200
            
    except Exception as e:
        current_app.logger.error(f"管理员解除用户管理员权限错误: {str(e)}")
        return jsonify({'code': 500, 'msg': '系统错误，请稍后重试', 'data': None}), 500


# 管理员接口：添加用户
@admin_bp.route('/users', methods=['POST'])
@admin_required
def add_user():
    """
    管理员添加新用户
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({
            'code': 400,
            'msg': '没有提供用户信息',
            'data': None
        }), 400
        
        # 验证必填字段
        username = data.get('username')
        password = data.get('password')
        
        if not username or len(username.strip()) == 0:
            return jsonify({
                'code': 400,
                'msg': '用户名不能为空',
                'data': None
            }), 400
        
        if not password or len(password) < 6:
            return jsonify({
                'code': 400,
                'msg': '密码长度不能少于6位',
                'data': None
            }), 400
        
        with Mysql() as mysql:
            # 检查用户名是否已存在
            existing_user = mysql.sql(
                "SELECT id FROM user WHERE username = %s AND deleted = 0",
                [username.strip()]
            )
            if existing_user:
                return jsonify({
                'code': 400,
                'msg': '用户名已存在',
                'data': None
            }), 400
            
            # 加密密码
            hashed_password = md5(password)
            
            # 添加用户
            mysql.sql(
                "INSERT INTO user (username, password) VALUES (%s, %s)",
                [username.strip(), hashed_password]
            )
            
            # 获取新添加的用户信息
            new_user = mysql.sql(
                "SELECT id, username, status, is_admin, create_time FROM user WHERE username = %s",
                [username.strip()]
            )
            
            current_app.logger.info(f"管理员添加新用户 {username.strip()} 成功")
            return jsonify({
                'code': 201,
                'msg': '添加用户成功',
                'data': new_user[0]
            }), 201
            
    except Exception as e:
        current_app.logger.error(f"管理员添加用户错误: {str(e)}")
        return jsonify({'code': 500, 'msg': '系统错误，请稍后重试', 'data': None}), 500


# 管理员接口：修改歌单信息
@admin_bp.route('/playlists/<int:playlist_id>', methods=['PUT'])
@admin_required
def update_playlist(playlist_id):
    """
    管理员修改歌单信息
    """
    try:
        with Mysql() as mysql:
            # 检查歌单是否存在
            playlist = mysql.sql(
                "SELECT id, user_id FROM playlist WHERE id = %s AND deleted = 0",
                [playlist_id]
            )
            
            if not playlist:
                return jsonify({'code': 404, 'msg': '歌单不存在', 'data': None}), 404
            
            # 获取请求数据
            data = request.get_json()
            if not data:
                return jsonify({
                'code': 400,
                'msg': '没有提供要修改的字段',
                'data': None
            }), 400
            
            # 允许修改的字段列表
            allowed_fields = ['name', 'cover_url', 'description']
            update_fields = []
            update_values = []
            
            # 构建更新语句
            for field, value in data.items():
                if field in allowed_fields:
                    # 处理name字段，确保不为空
                    if field == 'name':
                        if not value or len(value.strip()) == 0:
                            return jsonify({
                                'code': 400,
                                'msg': '歌单名称不能为空',
                                'data': None
                            }), 400
                        update_fields.append(f"{field} = %s")
                        update_values.append(value.strip())
                    # 处理cover_url和description字段，可以为空
                    else:
                        update_fields.append(f"{field} = %s")
                        update_values.append(value if value is not None else '')
            
            if not update_fields:
                return jsonify({
                'code': 400,
                'msg': '没有提供有效的字段进行修改',
                'data': None
            }), 400
            
            # 添加歌单ID到更新值列表
            update_values.append(playlist_id)
            
            # 执行更新
            update_query = f"UPDATE playlist SET {', '.join(update_fields)} WHERE id = %s AND deleted = 0"
            mysql.sql(update_query, update_values)
            
            # 获取更新后的歌单信息
            updated_playlist = mysql.sql(
                '''SELECT id, user_id, name, cover_url, description, create_time, update_time 
                 FROM playlist WHERE id = %s AND deleted = 0''',
                [playlist_id]
            )
            
            current_app.logger.info(f"管理员更新歌单 {playlist_id} 的信息成功")
            return jsonify({
                'code': 200,
                'msg': '更新歌单信息成功',
                'data': updated_playlist[0]
            }), 200
            
    except Exception as e:
        current_app.logger.error(f"管理员更新歌单信息错误: {str(e)}")
        return jsonify({'code': 500, 'msg': '系统错误，请稍后重试', 'data': None}), 500
