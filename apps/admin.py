from flask import Blueprint, request, jsonify, current_app, session, render_template
from werkzeug.security import check_password_hash
from functools import wraps
from apps.tool.Mysql import Mysql
import hashlib

# 创建admin蓝图
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# 管理页面路由
@admin_bp.route('/')
def admin_index():
    """
    渲染管理页面
    """
    return render_template('admin/index.html')

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




# 管理员接口：获取当前登录管理员信息
@admin_bp.route('/me', methods=['GET'])
@admin_required
def get_current_admin_info():
    """
    获取当前登录管理员信息接口
    """
    try:
        # 从session获取当前用户ID
        user_id = session.get('user_id')
        
        with Mysql() as mysql:
            # 查询管理员详细信息
            user = mysql.sql(
                "SELECT id, username, netease_user_id, status, is_admin, create_time, update_time "
                "FROM user WHERE id = %s AND deleted = 0",
                [user_id]
            )
            
            if not user:
                return jsonify({
                    'code': 404,
                    'msg': '管理员不存在',
                    'data': None
                }), 404
            
            current_app.logger.info(f"获取当前管理员信息成功: 用户ID {user_id}")
            
            return jsonify({
                'code': 200,
                'msg': '获取管理员信息成功',
                'data': user[0]
            }), 200
            
    except Exception as e:
        current_app.logger.error(f"获取管理员信息错误: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '系统错误，请稍后重试',
            'data': None
        }), 500


# 管理员接口：修改当前登录管理员的名称和密码
@admin_bp.route('/profile', methods=['PUT'])
@admin_required
def update_admin_profile():
    """
    修改当前登录管理员的名称和密码接口
    """
    try:
        # 从session获取当前管理员ID
        user_id = session.get('user_id')
        
        # 获取请求数据
        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')
        
        # 检查至少提供了一个需要修改的字段
        if not any([username, password]):
            return jsonify({
                'code': 400,
                'msg': '请至少提供一个需要修改的字段（用户名或密码）',
                'data': None
            }), 400
        
        with Mysql() as mysql:
            # 检查管理员是否存在
            admin = mysql.sql("SELECT id, username FROM user WHERE id = %s AND deleted = 0", [user_id])
            if not admin:
                return jsonify({
                    'code': 404,
                    'msg': '管理员不存在',
                    'data': None
                }), 404
            
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
                existing_admin = mysql.sql(
                    "SELECT id FROM user WHERE username=%s AND deleted=0 AND id!=%s",
                    [username, user_id]
                )
                if existing_admin:
                    return jsonify({
                        'code': 400,
                        'msg': '用户名已存在',
                        'data': None
                    }), 400
                    
                update_fields.append("username = %s")
                update_values.append(username)
                
                # 更新session中的用户名
                session['username'] = username
            
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
            
            if update_fields:
                # 添加更新时间
                update_fields.append("update_time = CURRENT_TIMESTAMP")
                
                # 构建完整的更新SQL
                update_sql = "UPDATE user SET " + ", ".join(update_fields) + " WHERE id = %s"
                update_values.append(user_id)
                
                # 执行更新
                mysql.sql(update_sql, update_values)
                
                current_app.logger.info(f"管理员修改自己的信息成功: 用户ID {user_id}")
                return jsonify({
                    'code': 200,
                    'msg': '修改管理员信息成功',
                    'data': None
                }), 200
            else:
                return jsonify({
                    'code': 400,
                    'msg': '没有可更新的字段',
                    'data': None
                }), 400
                
    except Exception as e:
        current_app.logger.error(f"管理员修改自己信息错误: {str(e)}")
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
    管理员获取所有用户列表（分页查询，支持多条件筛选）
    """
    try:
        # 获取分页参数
        current = request.args.get('current', 1, type=int)
        size = request.args.get('size', 10, type=int)
        
        # 获取查询条件
        username = request.args.get('username', '', type=str).strip()
        netease_user_id = request.args.get('netease_user_id', '', type=str).strip()
        status = request.args.get('status', None, type=int)
        is_admin = request.args.get('is_admin', None, type=int)
        
        # 计算偏移量
        offset = (current - 1) * size
        
        with Mysql() as mysql:
            # 构建查询条件
            conditions = []
            params = []
            
            if username:
                conditions.append("username LIKE %s")
                params.append(f"%{username}%")
            
            if netease_user_id:
                conditions.append("netease_user_id = %s")
                params.append(netease_user_id)
            
            if status is not None:
                conditions.append("status = %s")
                params.append(status)
            
            if is_admin is not None:
                conditions.append("is_admin = %s")
                params.append(is_admin)
            
            # 构建SQL查询
            where_clause = " AND ".join(conditions)
            where_clause = f" AND {where_clause}" if where_clause else ""
            
            # 查询当前页数据
            select_sql = f"SELECT id, username, netease_user_id, status, is_admin, create_time FROM user WHERE deleted = 0{where_clause} LIMIT %s OFFSET %s"
            users = mysql.sql(select_sql, params + [size, offset])
            
            # 查询总记录数
            count_sql = f"SELECT COUNT(*) as total FROM user WHERE deleted = 0{where_clause}"
            total_count = mysql.sql(count_sql, params)[0]['total']
            
            # 计算总页数
            total_pages = (total_count + size - 1) // size
            
            return jsonify({
                'code': 200,
                'msg': '获取用户列表成功',
                'data': {
                    'records': users,
                    'current': current,
                    'size': size,
                    'total': total_count,
                    'pages': total_pages
                }
            }), 200
    except Exception as e:
        current_app.logger.error(f"获取用户列表错误: {str(e)}")
        return jsonify({'message': '系统错误，请稍后重试'}), 500


# 管理员接口：根据多条件搜索用户
@admin_bp.route('/users/search', methods=['GET'])
@admin_required
def search_users_by_username():
    """
    管理员根据多条件搜索用户（分页查询）
    """
    try:
        # 获取搜索参数
        username = request.args.get('username', '', type=str).strip()
        netease_user_id = request.args.get('netease_user_id', '', type=str).strip()
        status = request.args.get('status', None, type=int)
        is_admin = request.args.get('is_admin', None, type=int)
        
        # 获取分页参数
        current = request.args.get('current', 1, type=int)
        size = request.args.get('size', 10, type=int)
        
        # 计算偏移量
        offset = (current - 1) * size
        
        # 构建查询条件
        conditions = []
        params = []
        
        if username:
            conditions.append("username LIKE %s")
            params.append(f"%{username}%")
        
        if netease_user_id:
            conditions.append("netease_user_id = %s")
            params.append(netease_user_id)
        
        if status is not None:
            conditions.append("status = %s")
            params.append(status)
        
        if is_admin is not None:
            conditions.append("is_admin = %s")
            params.append(is_admin)
        
        # 构建SQL查询
        where_clause = " AND ".join(conditions)
        where_clause = f" AND {where_clause}" if where_clause else ""
        
        with Mysql() as mysql:
            # 查询当前页数据
            select_sql = f"SELECT id, username, netease_user_id, status, is_admin, create_time FROM user WHERE deleted = 0{where_clause} LIMIT %s OFFSET %s"
            users = mysql.sql(select_sql, params + [size, offset])
            
            # 查询总记录数
            count_sql = f"SELECT COUNT(*) as total FROM user WHERE deleted = 0{where_clause}"
            total_count = mysql.sql(count_sql, params)[0]['total']
            
            # 计算总页数
            total_pages = (total_count + size - 1) // size
            
            # 记录搜索条件日志
            search_conditions = []
            if username:
                search_conditions.append(f"用户名: {username}")
            if netease_user_id:
                search_conditions.append(f"网易云ID: {netease_user_id}")
            if status is not None:
                search_conditions.append(f"状态: {status}")
            if is_admin is not None:
                search_conditions.append(f"是否管理员: {is_admin}")
            current_app.logger.info(f"管理员搜索用户成功，搜索条件: {', '.join(search_conditions)}，找到 {total_count} 个用户")
            
            return jsonify({
                'code': 200,
                'msg': '搜索用户成功',
                'data': {
                    'records': users,
                    'current': current,
                    'size': size,
                    'total': total_count,
                    'pages': total_pages
                }
            }), 200
    except Exception as e:
        current_app.logger.error(f"搜索用户错误: {str(e)}")
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


# 管理员接口：添加用户
@admin_bp.route('/users', methods=['POST'])
@admin_required
def add_user():
    """
    管理员添加新用户
    """
    try:
        # 获取当前管理员ID
        current_admin_id = session.get('user_id')
        
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
        
        # 检查是否要添加管理员
        is_admin = data.get('is_admin', 0)
        if is_admin and current_admin_id != 1:
            return jsonify({
                'code': 403,
                'msg': '只有ID为1的管理员可以添加管理员',
                'data': None
            }), 403
        
        # 获取网易用户ID
        netease_user_id = data.get('netease_user_id')
        
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
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # 添加用户
            mysql.sql(
                "INSERT INTO user (username, password, is_admin, netease_user_id) VALUES (%s, %s, %s, %s)",
                [username.strip(), hashed_password, is_admin, netease_user_id]
            )
            
            # 获取新添加的用户信息
            new_user = mysql.sql(
                "SELECT id, username, status, is_admin, netease_user_id, create_time FROM user WHERE username = %s",
                [username.strip()]
            )
            
            current_app.logger.info(f"管理员添加新用户 {username.strip()} 成功")
            return jsonify({
                'code': 200,
                'msg': '添加用户成功',
                'data': new_user[0]
            }), 200
            
    except Exception as e:
        current_app.logger.error(f"管理员添加用户错误: {str(e)}")
        return jsonify({'code': 500, 'msg': '系统错误，请稍后重试', 'data': None}), 500


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
            user = mysql.sql(
                "SELECT id, is_admin FROM user WHERE id = %s AND deleted = 0",
                [target_user_id]
            )
            if not user:
                return jsonify({
                'code': 404,
                'msg': '用户不存在',
                'data': None
            }), 404
            
            # 检查要删除的用户是否是管理员
            if user[0]['is_admin'] == 1:
                # 只有ID为1的管理员可以删除其他管理员
                if current_user_id != 1:
                    return jsonify({
                        'code': 403,
                        'msg': '只有ID为1的管理员可以删除其他管理员',
                        'data': None
                    }), 403
            
            # 逻辑删除用户
            delete_sql = f"UPDATE user SET deleted = 1 WHERE id = {target_user_id}"
            result = mysql.sql(delete_sql)
            
            # 检查删除用户是否成功
            if not (isinstance(result, tuple) and result[0] is not None and result[0] > 0):
                return jsonify({
                    'code': 500,
                    'msg': '删除用户失败',
                    'data': None
                }), 500
            
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


# 管理员接口：聚合修改用户信息（名称、密码、网易云ID、管理员权限、封禁状态）
@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_single_user(user_id):
    """
    管理员聚合修改用户信息的接口，支持同时或单独修改以下字段：
    - username: 用户名（必填，唯一）
    - password: 密码（必填）
    - netease_user_id: 网易云用户ID（可清空）
    - is_admin: 是否管理员（0或1）
    - status: 是否封禁（0或1，0表示正常，1表示封禁）
    """
    try:
        with Mysql() as mysql:
            # 获取当前管理员ID
            current_admin_id = session.get('user_id')
            
            # 检查用户是否存在
            user = mysql.sql(
                "SELECT id, username, is_admin FROM user WHERE id = %s AND deleted = 0",
                [user_id]
            )
            
            if not user:
                return jsonify({'code': 404, 'msg': '用户不存在', 'data': None}), 404
            
            # 检查要修改的用户是否是管理员
            if user[0]['is_admin'] == 1:
                # 只有ID为1的管理员可以修改其他管理员的信息
                if current_admin_id != 1:
                    return jsonify({
                        'code': 403,
                        'msg': '只有ID为1的管理员可以修改其他管理员的信息',
                        'data': None
                    }), 403
            
            # 获取请求数据
            data = request.get_json()
            if not data:
                return jsonify({
                'code': 400,
                'msg': '没有提供要修改的字段',
                'data': None
            }), 400
            
            # 允许修改的字段列表
            allowed_fields = ['username', 'status', 'is_admin', 'password', 'netease_user_id']
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
                    # 处理password字段
                    elif field == 'password':
                        if not value or len(value.strip()) == 0:
                            return jsonify({
                            'code': 400,
                            'msg': '密码不能为空',
                            'data': None
                        }), 400
                        # 对密码进行哈希处理
                        hashed_password = hashlib.sha256(value.strip().encode()).hexdigest()
                        update_fields.append(f"{field} = %s")
                        update_values.append(hashed_password)
                    # 处理netease_user_id字段
                    elif field == 'netease_user_id':
                        if value == "":
                            # 允许清空网易云ID
                            update_fields.append(f"{field} = NULL")
                        else:
                            update_fields.append(f"{field} = %s")
                            update_values.append(value)
            
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
            
            # 记录实际修改的字段
            current_app.logger.info(f"管理员更新用户 {user_id} 的信息成功，修改字段: {', '.join([field.split(' =')[0] for field in update_fields])}")
            return jsonify({
                'code': 200,
                'msg': '更新用户信息成功',
                'data': updated_user[0]
            }), 200
            
    except Exception as e:
        current_app.logger.error(f"管理员更新用户信息错误: {str(e)}")
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
            
            # 检查解放用户是否成功
            if not (isinstance(result, tuple) and result[0] is not None and result[0] > 0):
                return jsonify({
                    'code': 500,
                    'msg': '解放用户失败',
                    'data': None
                }), 500
            
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
        # 获取当前管理员ID
        current_admin_id = session.get('user_id')
        
        # 只有ID为1的管理员可以设置其他用户为管理员
        if current_admin_id != 1:
            return jsonify({
                'code': 403,
                'msg': '只有ID为1的管理员可以设置其他用户为管理员',
                'data': None
            }), 403
        
        with Mysql() as mysql:
            # 检查用户是否存在
            select_sql = f"SELECT id FROM user WHERE id = {target_user_id} AND deleted = 0"
            user = mysql.sql(select_sql)
            if not user:
                return jsonify({'code': 404, 'msg': '用户不存在', 'data': None}), 404
            
            # 设置为管理员
            set_admin_sql = f"UPDATE user SET is_admin = 1 WHERE id = {target_user_id}"
            result = mysql.sql(set_admin_sql)
            
            # 检查设置管理员是否成功
            if not (isinstance(result, tuple) and result[0] is not None and result[0] > 0):
                return jsonify({
                    'code': 500,
                    'msg': '设置用户为管理员失败',
                    'data': None
                }), 500
            
            return jsonify({
                'code': 200,
                'msg': '设置用户为管理员成功',
                'data': None
            }), 200
    except Exception as e:
        current_app.logger.error(f"设置用户为管理员错误: {str(e)}")
        return jsonify({'code': 500, 'msg': '系统错误，请稍后重试', 'data': None}), 500

# 管理员接口：解除管理员权限
@admin_bp.route('/users/<int:user_id>/remove-admin', methods=['POST'])
@admin_required
def remove_admin(user_id):
    """
    管理员解除指定用户的管理员权限
    """
    try:
        # 获取当前管理员ID
        current_admin_id = session.get('user_id')
        
        # 只有ID为1的管理员可以解除其他管理员的权限
        if current_admin_id != 1:
            return jsonify({
                'code': 403,
                'msg': '只有ID为1的管理员可以解除其他管理员的权限',
                'data': None
            }), 403
        
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
            result = mysql.sql(
                "UPDATE user SET is_admin = 0 WHERE id = %s AND deleted = 0",
                [user_id]
            )
            
            # 检查解除管理员权限是否成功
            if not (isinstance(result, tuple) and result[0] is not None and result[0] > 0):
                return jsonify({
                    'code': 500,
                    'msg': '解除管理员权限失败',
                    'data': None
                }), 500
            
            current_app.logger.info(f"管理员解除用户 {user_id} 的管理员权限成功")
            return jsonify({
                'code': 200,
                'msg': '解除管理员权限成功',
                'data': None
            }), 200
            
    except Exception as e:
        current_app.logger.error(f"管理员解除用户管理员权限错误: {str(e)}")
        return jsonify({'code': 500, 'msg': '系统错误，请稍后重试', 'data': None}), 500




# 管理员接口：获取所有歌单
@admin_bp.route('/playlists', methods=['GET'])
@admin_required
def get_all_playlists():
    """
    管理员获取所有歌单（分页查询）
    参数：
        current: 当前页码，默认1
        size: 每页数量，默认10
        name: 歌单名称模糊查询
        username: 创建人名称模糊查询
    """
    try:
        # 获取分页参数
        current = request.args.get('current', 1, type=int)
        size = request.args.get('size', 10, type=int)
        
        # 获取查询参数
        name = request.args.get('name')
        username = request.args.get('username')
        
        # 计算偏移量
        offset = (current - 1) * size
        
        with Mysql() as mysql:
            # 构建查询条件
            conditions = ["p.deleted=0"]
            params = []
            
            if name:
                conditions.append("p.name LIKE %s")
                params.append(f"%{name}%")
            
            if username:
                conditions.append("u.username LIKE %s")
                params.append(f"%{username}%")
            
            # 添加分页参数
            params.extend([size, offset])
            
            # 查询当前页数据
            playlists = mysql.sql(
                f'''SELECT p.id as playlist_id, p.user_id as id, u.username, p.name, p.cover_url, p.description, p.create_time, p.update_time,
                       COUNT(ps.song_id) as song_count
                FROM playlist p
                LEFT JOIN user u ON p.user_id = u.id
                LEFT JOIN playlist_song ps ON p.id = ps.playlist_id
                WHERE {' AND '.join(conditions)}
                GROUP BY p.id
                ORDER BY p.create_time DESC
                LIMIT %s OFFSET %s''',
                params
            )
            
            # 查询总记录数
            if conditions:
                count_sql = f"SELECT COUNT(*) as total FROM playlist p LEFT JOIN user u ON p.user_id = u.id WHERE {' AND '.join(conditions)}"
                total_count = mysql.sql(count_sql, params[:-2])[0]['total']  # 排除分页参数
            else:
                count_sql = "SELECT COUNT(*) as total FROM playlist WHERE deleted = 0"
                total_count = mysql.sql(count_sql)[0]['total']
            
            # 计算总页数
            total_pages = (total_count + size - 1) // size
            
            current_app.logger.info(f"管理员获取所有歌单成功: 用户ID {session.get('user_id')}，当前页 {current}，每页 {size} 条，共 {total_count} 个歌单")
            return jsonify({
                'code': 200,
                'msg': '获取所有歌单成功',
                'data': {
                    'records': playlists,
                    'current': current,
                    'size': size,
                    'total': total_count,
                    'pages': total_pages
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
