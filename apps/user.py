from flask import Blueprint, request, redirect, url_for, session, jsonify, current_app, render_template
from apps.tool.Mysql import Mysql
import hashlib
from functools import wraps
from apps.music import get_songs_detail
import re


# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('index', page_name='login'))
        return f(*args, **kwargs)

    return decorated_function


# 管理员权限验证装饰器
def admin_required(f):
    """
    管理员权限验证装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'message': '请先登录'}), 401
        if not session.get('is_admin'):
            return jsonify({'message': '需要管理员权限'}), 403
        return f(*args, **kwargs)
    return decorated_function

# 注册蓝图
user = Blueprint('user', __name__, url_prefix='/user')

# 用户输入验证函数（增强防注入）
def validate_user_input(username, password, confirm_password=None):
    """验证用户输入"""
    # 如果用户名和密码都为空，返回错误
    if not username and not password:
        return '用户名和密码不能为空'
    
    # 如果只传入了用户名，则只验证用户名
    if username and not password:
        pass  # 跳过密码验证
    
    # 如果只传入了密码，则只验证密码
    elif not username and password:
        pass  # 跳过用户名验证
    
    # 如果两者都传入了，则都验证
    else:
        if not username or not password:
            return '用户名和密码不能为空'

    # 验证用户名（如果提供了）
    if username:
        # 检测非法字符，防止注入
        if re.search(r'[<>"\'%;()&+\\\/\[\]{}*\?\|^~`]', username):
            return '用户名包含非法字符'

        if len(username) < 3 or len(username) > 20:
            return '用户名长度应在3-20个字符之间'

    # 验证密码（如果提供了）
    if password:
        if len(password) < 6 or len(password) > 20:
            return '密码长度应在6-20个字符之间'

        if confirm_password and password != confirm_password:
            return '两次输入的密码不一致'

    return None

# 登录接口
@user.route('/login', methods=['POST'])
def login():
    # 统一获取用户名和密码
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    # 使用统一验证函数
    error = validate_user_input(username, password)
    if error:
        return jsonify({'message': error}), 400

    # 密码加密处理
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        with Mysql() as mysql:
            # 先查询用户是否存在（不考虑密码，只检查用户名和未删除状态）
            user_exists = mysql.sql(
                "SELECT id, username, status FROM user WHERE username=%s AND deleted=0",
                [username]
            )
            
            # 检查用户是否存在
            if not isinstance(user_exists, list) or len(user_exists) == 0:
                current_app.logger.warning(f"用户登录失败 - 用户不存在: {username}")
                return jsonify({'message': '用户不存在'}), 401
            
            # 检查用户状态是否正常
            user = user_exists[0]
            if user['status'] != 0:
                current_app.logger.warning(f"用户登录失败 - 账号已被禁用: {username}")
                return jsonify({'message': '账号已被禁用'}), 401
            
            # 用户存在且状态正常，检查密码是否正确
            user_list = mysql.sql(
                "SELECT id, username, netease_user_id, is_admin FROM user WHERE username=%s AND password=%s AND deleted=0 AND status=0",
                [username, hashed_password]
            )

            # 检查密码是否正确
            if isinstance(user_list, list) and len(user_list) > 0:
                # 设置用户会话
                current_app.logger.info(f"用户登录成功: {username}")
                session.permanent = True  # 启用持久化session
                session['user_id'] = user_list[0]['id']
                session['username'] = user_list[0]['username']
                session['netease_user_id'] = user_list[0]['netease_user_id']
                session['is_admin'] = user_list[0]['is_admin']
                return jsonify({'message': '登录成功'}), 200
            else:
                current_app.logger.warning(f"用户登录失败 - 密码错误: {username}")
                return jsonify({'message': '密码错误'}), 401

    except Exception as e:
        # 记录详细错误日志
        current_app.logger.error(f"登录错误: {str(e)}")
        return jsonify({'message': '系统错误，请稍后重试'}), 500


# 注册接口
@user.route('/register', methods=['POST'])
def register():
    # 获取注册信息
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()

    # 使用统一验证函数
    error = validate_user_input(username, password, confirm_password)
    if error:
        return jsonify({'message': error}), 400

    try:
        with Mysql() as mysql:
            # 检查用户名是否已存在，考虑逻辑删除和用户状态
            existing_user = mysql.sql(
                "SELECT id FROM user WHERE username=%s AND deleted=0 AND status=0",
                [username]
            )

            if isinstance(existing_user, list) and len(existing_user) > 0:
                return jsonify({'message': '用户名已存在'}), 400

            # 插入新用户
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            result = mysql.sql(
                "INSERT INTO user (username, password) VALUES (%s, %s)",
                [username, hashed_password]
            )

            if isinstance(result, tuple) and result[0] > 0:
                return jsonify({'message': '注册成功，请登录'}), 200
            else:
                return jsonify({'message': '注册失败，请重试'}), 500

    except Exception as e:
        current_app.logger.error(f"注册错误: {str(e)}")
        return jsonify({'message': '系统错误，请稍后重试'}), 500


# 注销接口
@user.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('index'))

# 修改个人信息页面
@user.route('/edit_profile')
@login_required
def edit_profile():
    try:
        user_id = session.get('user_id')
        with Mysql() as mysql:
            # 获取当前用户信息
            user_info = mysql.sql("SELECT username, netease_user_id FROM user WHERE id = %s", [user_id])
            if user_info and isinstance(user_info, list) and len(user_info) > 0:
                username = user_info[0].get('username', '')
                netease_user_id = user_info[0].get('netease_user_id', '')
                return render_template('user/edit_profile.html', username=username, netease_user_id=netease_user_id)
    except Exception as e:
        current_app.logger.error(f"获取用户信息失败: {e}")
    return render_template('user/edit_profile.html')

# 创建歌单接口
@user.route('/create_playlist', methods=['POST'])
@login_required
def create_playlist():
    """
    创建歌单
    POST参数: name (歌单名称), cover_url (歌单封面), description (歌单描述)
    """
    try:
        user_id = session.get('user_id')
        
        # 添加详细日志记录接收到的数据
        current_app.logger.info(f"接收到的请求头: {dict(request.headers)}")
        current_app.logger.info(f"是否有JSON数据: {request.is_json}")
        current_app.logger.info(f"表单数据: {dict(request.form)}")
        current_app.logger.info(f"文件数据: {list(request.files.keys())}")
        
        # 尝试获取JSON数据，如果没有则尝试从表单获取
        data = request.json or {}
        if not data:
            current_app.logger.info("未获取到JSON数据，尝试从表单获取")
            data = dict(request.form)
        
        # 获取参数并验证
        name = data.get('name', '').strip()
        current_app.logger.info(f"获取到的歌单名称: {name}")
        
        if not name:
            current_app.logger.warning("歌单名称为空")
            return jsonify({'message': '歌单名称不能为空'}), 400
        
        if len(name) > 100:
            current_app.logger.warning(f"歌单名称过长: {name}")
            return jsonify({'message': '歌单名称长度不能超过100个字符'}), 400
        
        # 获取cover_url，不再限制长度（数据库已修改为TEXT类型）
        cover_url = data.get('cover_url', '')
        current_app.logger.info(f"获取到的封面URL长度: {len(cover_url)}, 前100字符: {cover_url[:100]}...")
        
        description = data.get('description', '')
        current_app.logger.info(f"获取到的描述: {description}")
        
        # 创建歌单
        with Mysql() as mysql:
            # 检查用户是否已存在同名歌单，添加逻辑删除条件
            existing = mysql.sql(
                "SELECT id FROM playlist WHERE user_id = %s AND name = %s AND deleted=0",
                [user_id, name]
            )
            
            if isinstance(existing, list) and existing:
                return jsonify({'message': '歌单名称已存在'}), 400
            
            # 插入新歌单
            result = mysql.sql(
                "INSERT INTO playlist (user_id, name, cover_url, description) VALUES (%s, %s, %s, %s)",
                [user_id, name, cover_url, description]
            )
            
            # 简化成功条件判断 - mysql.update返回 (影响行数, 自增ID)
            current_app.logger.info(f"插入结果: {result}, 类型: {type(result)}")
            
            # 检查是否成功插入（影响行数>0）
            if isinstance(result, tuple) and len(result) >= 1 and result[0] > 0:
                # 使用mysql工具类返回的rowid作为歌单ID
                playlist_id = result[1] if len(result) > 1 and result[1] is not None else None
                
                # 如果没有获取到rowid，再尝试通过LAST_INSERT_ID()获取
                if playlist_id is None:
                    last_id_result = mysql.sql("SELECT LAST_INSERT_ID() as id")
                    if isinstance(last_id_result, list) and last_id_result and 'id' in last_id_result[0]:
                        playlist_id = last_id_result[0]['id']
                    else:
                        current_app.logger.error("获取新创建的歌单ID失败")
                        return jsonify({'message': '歌单创建失败：无法获取歌单ID'}), 500
                
                current_app.logger.info(f"用户 {user_id} 创建歌单成功: {name} (ID: {playlist_id})")
                return jsonify({
                    'message': '歌单创建成功',
                    'playlist_id': playlist_id
                }), 200
            else:
                return jsonify({'message': '歌单创建失败'}), 500
                
    except Exception as e:
        current_app.logger.error(f"创建歌单错误: {str(e)}")
        return jsonify({'message': '系统错误，请稍后重试'}), 500

# 获取歌单列表接口
@user.route('/playlists', methods=['GET'])
@login_required
def get_playlists():
    """
    获取用户的所有歌单列表
    """
    try:
        user_id = session.get('user_id')
        
        with Mysql() as mysql:
            # 查询用户的所有歌单，添加逻辑删除条件
            playlists = mysql.sql(
                """
                SELECT p.id, p.name, p.cover_url, p.description, p.create_time, p.update_time,
                       COUNT(ps.song_id) as song_count
                FROM playlist p
                LEFT JOIN playlist_song ps ON p.id = ps.playlist_id
                WHERE p.user_id = %s AND p.deleted=0
                GROUP BY p.id
                ORDER BY p.create_time DESC
                """,
                [user_id]
            )
            
            current_app.logger.info(f"用户 {user_id} 获取歌单列表成功")
            return jsonify({
                'playlists': playlists,
                'total': len(playlists)
            }), 200
            
    except Exception as e:
        current_app.logger.error(f"获取歌单列表错误: {str(e)}")
        return jsonify({'message': '系统错误，请稍后重试'}), 500

# 获取歌单详情接口
@user.route('/playlist/<int:playlist_id>', methods=['GET'])
@login_required
def get_playlist_detail(playlist_id):
    """
    获取歌单详情，包括歌单中的歌曲
    """
    try:
        user_id = session.get('user_id')
        
        with Mysql() as mysql:
            # 首先检查歌单是否存在且属于当前用户，添加逻辑删除条件
            playlist = mysql.sql(
                "SELECT id, name, cover_url, description, create_time, update_time FROM playlist WHERE id = %s AND user_id = %s AND deleted=0",
                [playlist_id, user_id]
            )
            
            if not (isinstance(playlist, list) and playlist):
                return jsonify({'message': '歌单不存在或无权访问'}), 404
            
            # 获取歌单中的歌曲
            songs = mysql.sql(
                """
                SELECT ps.song_id, ps.add_time
                FROM playlist_song ps
                WHERE ps.playlist_id = %s
                ORDER BY ps.add_time DESC
                """,
                [playlist_id]
            )
            
            # 批量获取歌曲详情（优化性能）
            enriched_songs = []
            try:
                # 如果没有歌曲，直接返回空列表
                if not songs:
                    enriched_songs = []
                else:
                    # 提取所有歌曲ID
                    song_ids = [song_info['song_id'] for song_info in songs]
                    # 按批次处理，避免单次请求过多ID（每批最多50个）
                    batch_size = 50
                    all_song_details = {}
                    
                    for i in range(0, len(song_ids), batch_size):
                        batch_ids = song_ids[i:i+batch_size]
                        # 批量获取这一批歌曲的详情
                        batch_result = get_songs_detail(batch_ids)
                        
                        if batch_result.get('code') == 200 and batch_result.get('songs'):
                            # 将结果存入字典，以song_id为key
                            for song in batch_result['songs']:
                                if song:
                                    all_song_details[song.get('id')] = song
                    
                    # 构建返回结果，保持原有顺序
                    for song_info in songs:
                        song_id = song_info['song_id']
                        # 查找是否有该歌曲的详情
                        song = all_song_details.get(song_id)
                        
                        if song:
                            # 有详情时构建丰富的歌曲信息
                            enriched_song = {
                                'song_id': song_id,
                                'add_time': song_info['add_time'],
                                'name': song.get('name', '未知歌曲'),
                                'artist': '/'.join([ar.get('name', '') for ar in song.get('ar', []) if ar.get('name')]),
                                'cover_url': song.get('al', {}).get('picUrl', ''),
                                'album': song.get('al', {}).get('name', '未知专辑')
                            }
                        else:
                            # 没有详情时使用基本信息
                            enriched_song = {
                                'song_id': song_id,
                                'add_time': song_info['add_time'],
                                'name': f'歌曲ID: {song_id}',
                                'artist': '未知歌手',
                                'cover_url': '',
                                'album': '未知专辑'
                            }
                        
                        enriched_songs.append(enriched_song)
                        
            except Exception as e:
                current_app.logger.error(f"批量获取歌曲详情失败: {str(e)}")
                # 出错时构建基本信息的歌曲列表
                enriched_songs = [
                    {
                        'song_id': song_info['song_id'],
                        'add_time': song_info['add_time'],
                        'name': f'歌曲ID: {song_info["song_id"]}',
                        'artist': '未知歌手',
                        'cover_url': '',
                        'album': '未知专辑'
                    }
                    for song_info in songs
                ]
            
            current_app.logger.info(f"用户 {user_id} 获取歌单详情成功: ID {playlist_id}")
            return jsonify({
                'playlist': playlist[0],
                'songs': enriched_songs,
                'song_count': len(enriched_songs)
            }), 200
            
    except Exception as e:
        current_app.logger.error(f"获取歌单详情错误: {str(e)}")
        return jsonify({'message': '系统错误，请稍后重试'}), 500

# 添加歌曲到歌单接口
@user.route('/playlist/<int:playlist_id>/add_song', methods=['POST'])
@login_required
def add_song_to_playlist(playlist_id):
    """
    添加歌曲到歌单
    POST参数: song_id (歌曲ID)
    """
    try:
        user_id = session.get('user_id')
        data = request.json or {}
        
        # 获取歌曲ID并验证
        song_id = data.get('song_id')
        if not song_id:
            return jsonify({'message': '歌曲ID不能为空'}), 400
        
        try:
            song_id = int(song_id)
            # 限制song_id的范围，确保不会超出MySQL BIGINT类型的范围
            if song_id < -9223372036854775808 or song_id > 9223372036854775807:
                return jsonify({'message': '歌曲ID超出有效范围'}), 400
        except ValueError:
            return jsonify({'message': '歌曲ID格式错误'}), 400
        
        with Mysql() as mysql:
            # 首先检查歌单是否存在，根据用户权限决定是否检查归属
            is_admin = session.get('is_admin', 0)
            if is_admin:
                # 管理员可以修改任意歌单
                playlist = mysql.sql(
                    "SELECT id FROM playlist WHERE id = %s AND deleted=0",
                    [playlist_id]
                )
            else:
                # 普通用户只能修改自己的歌单
                playlist = mysql.sql(
                    "SELECT id FROM playlist WHERE id = %s AND user_id = %s AND deleted=0",
                    [playlist_id, user_id]
                )
            
            if not (isinstance(playlist, list) and playlist):
                return jsonify({'message': '歌单不存在或无权访问'}), 404
            
            # 检查歌曲是否已在歌单中
            existing = mysql.sql(
                "SELECT id FROM playlist_song WHERE playlist_id = %s AND song_id = %s",
                [playlist_id, song_id]
            )
            
            if isinstance(existing, list) and existing:
                return jsonify({'message': '歌曲已在歌单中'}), 400
            
            # 添加歌曲到歌单
            result = mysql.sql(
                "INSERT INTO playlist_song (playlist_id, song_id) VALUES (%s, %s)",
                [playlist_id, song_id]
            )
            
            if isinstance(result, tuple) and result[0] > 0:
                # 更新歌单的更新时间
                mysql.sql(
                    "UPDATE playlist SET update_time = CURRENT_TIMESTAMP WHERE id = %s",
                    [playlist_id]
                )
                
                current_app.logger.info(f"用户 {user_id} 添加歌曲 {song_id} 到歌单 {playlist_id} 成功")
                return jsonify({'message': '歌曲添加成功'}), 200
            else:
                return jsonify({'message': '歌曲添加失败'}), 500
                
    except Exception as e:
        current_app.logger.error(f"添加歌曲到歌单错误: {str(e)}")
        return jsonify({'message': '系统错误，请稍后重试'}), 500

# 删除歌单中的歌曲接口
@user.route('/playlist/<int:playlist_id>/remove_song/<int:song_id>', methods=['DELETE'])
@login_required
def remove_song_from_playlist(playlist_id, song_id):
    """
    从歌单中删除歌曲
    """
    try:
        user_id = session.get('user_id')
        
        # 验证song_id格式
        if not isinstance(song_id, int):
            return jsonify({'message': '歌曲ID格式错误'}), 400
        
        with Mysql() as mysql:
            # 检查歌单是否存在
            if session.get('is_admin'):
                # 管理员可以修改任意歌单
                playlist = mysql.sql(
                    "SELECT id FROM playlist WHERE id = %s AND deleted=0",
                    [playlist_id]
                )
            else:
                # 普通用户只能修改自己的歌单
                playlist = mysql.sql(
                    "SELECT id FROM playlist WHERE id = %s AND user_id = %s AND deleted=0",
                    [playlist_id, user_id]
                )
            
            if not (isinstance(playlist, list) and playlist):
                return jsonify({'message': '歌单不存在或无权访问'}), 404
            
            # 检查歌曲是否在歌单中
            existing = mysql.sql(
                "SELECT id FROM playlist_song WHERE playlist_id = %s AND song_id = %s",
                [playlist_id, song_id]
            )
            
            if not (isinstance(existing, list) and existing):
                return jsonify({'message': '歌曲不在歌单中'}), 404
            
            # 从歌单中删除歌曲
            result = mysql.sql(
                "DELETE FROM playlist_song WHERE playlist_id = %s AND song_id = %s",
                [playlist_id, song_id]
            )
            
            if isinstance(result, int) and result > 0:
                # 更新歌单的更新时间
                mysql.sql(
                    "UPDATE playlist SET update_time = CURRENT_TIMESTAMP WHERE id = %s",
                    [playlist_id]
                )
                
                current_app.logger.info(f"用户 {user_id} 从歌单 {playlist_id} 中删除歌曲 {song_id} 成功")
                return jsonify({'message': '歌曲删除成功'}), 200
            else:
                return jsonify({'message': '歌曲删除失败'}), 500
                
    except Exception as e:
        current_app.logger.error(f"从歌单删除歌曲错误: {str(e)}")
        return jsonify({'message': '系统错误，请稍后重试'}), 500

# 更新歌单接口
@user.route('/playlist/<int:playlist_id>', methods=['PUT'])
@login_required
def update_playlist(playlist_id):
    """
    修改歌单信息
    PUT参数: name (歌单名称), cover_url (歌单封面URL)
    """
    try:
        user_id = session.get('user_id')
        data = request.json or {}
        
        # 获取要更新的字段
        name = data.get('name')
        cover_url = data.get('cover_url')
        
        # 验证参数 - 至少提供一个字段进行更新
        if name is None and cover_url is None:
            return jsonify({'message': '请提供要更新的歌单名称或封面'}), 400
        
        # 验证歌单名称
        if name is not None:
            if not isinstance(name, str):
                return jsonify({'message': '歌单名称格式错误'}), 400
            name = name.strip()
            if not name:
                return jsonify({'message': '歌单名称不能为空'}), 400
            if len(name) > 100:
                return jsonify({'message': '歌单名称长度不能超过100个字符'}), 400
        
        # 验证封面URL
        if cover_url is not None:
            if not isinstance(cover_url, str):
                return jsonify({'message': '封面URL格式错误'}), 400
            # 不再限制封面URL长度（数据库已修改为TEXT类型）
        
        with Mysql() as mysql:
            # 首先检查歌单是否存在且属于当前用户，添加逻辑删除条件
            playlist = mysql.sql(
                "SELECT id FROM playlist WHERE id = %s AND user_id = %s AND deleted=0",
                [playlist_id, user_id]
            )
            
            if not (isinstance(playlist, list) and playlist):
                return jsonify({'message': '歌单不存在或无权访问'}), 404
            
            # 构建更新语句
            update_fields = []
            params = []
            
            if name is not None:
                update_fields.append("name = %s")
                params.append(name)
            
            if cover_url is not None:
                update_fields.append("cover_url = %s")
                params.append(cover_url)
            
            # 添加更新时间
            update_fields.append("update_time = CURRENT_TIMESTAMP")
            
            # 添加playlist_id到参数列表
            params.append(playlist_id)
            
            # 执行更新
            sql = f"UPDATE playlist SET {', '.join(update_fields)} WHERE id = %s"
            result = mysql.sql(sql, params)
            
            # Mysql.sql方法执行update时返回元组(count, rowid)
            if isinstance(result, tuple) and len(result) > 0 and result[0] > 0:
                current_app.logger.info(f"用户 {user_id} 更新歌单 {playlist_id} 信息成功")
                return jsonify({'message': '歌单信息更新成功'}), 200
            else:
                return jsonify({'message': '歌单信息更新失败'}), 500
                
    except Exception as e:
        current_app.logger.error(f"更新歌单信息错误: {str(e)}")
        return jsonify({'message': '系统错误，请稍后重试'}), 500

# 删除歌单接口
@user.route('/playlist/<int:playlist_id>', methods=['DELETE'])
@login_required
def delete_playlist(playlist_id):
    """
    删除歌单
    级联删除歌单中的所有歌曲记录
    """
    try:
        user_id = session.get('user_id')
        
        with Mysql() as mysql:
            # 首先检查歌单是否存在，根据用户权限决定是否检查归属
            if session.get('is_admin'):
                # 管理员可以删除任意歌单
                playlist = mysql.sql(
                    "SELECT id, name FROM playlist WHERE id = %s AND deleted=0",
                    [playlist_id]
                )
            else:
                # 普通用户只能删除自己的歌单
                playlist = mysql.sql(
                    "SELECT id, name FROM playlist WHERE id = %s AND user_id = %s AND deleted=0",
                    [playlist_id, user_id]
                )
            
            if not (isinstance(playlist, list) and playlist):
                return jsonify({'message': '歌单不存在或无权访问'}), 404
            
            playlist_name = playlist[0].get('name', '')
            
            # 使用逻辑删除代替物理删除
            if session.get('is_admin'):
                # 管理员可以删除任意歌单
                playlist_delete_result = mysql.sql(
                    "UPDATE playlist SET deleted=1 WHERE id = %s",
                    [playlist_id]
                )
            else:
                # 普通用户只能删除自己的歌单
                playlist_delete_result = mysql.sql(
                    "UPDATE playlist SET deleted=1 WHERE id = %s AND user_id = %s",
                    [playlist_id, user_id]
                )
            
            # 检查删除是否成功
            if isinstance(playlist_delete_result, tuple) and len(playlist_delete_result) > 0 and playlist_delete_result[0] > 0:
                current_app.logger.info(f"用户 {user_id} 删除歌单成功: ID {playlist_id}, 名称 '{playlist_name}'")
                return jsonify({'message': '歌单删除成功'}), 200
            else:
                return jsonify({'message': '歌单删除失败'}), 500
                
    except Exception as e:
        current_app.logger.error(f"删除歌单错误: {str(e)}")
        return jsonify({'message': '系统错误，请稍后重试'}), 500

# 保存播放历史接口
@user.route('/save_history', methods=['POST'])
@login_required
def save_play_history():
    """
    保存用户播放历史（去重并更新时间）
    """
    try:
        # 获取用户ID
        user_id = session.get('user_id')
        
        # 获取歌曲ID
        song_id = request.json.get('song_id')
        
        if not song_id:
            return jsonify({'message': '歌曲ID不能为空'}), 400
        
        # 确保song_id是整数
        try:
            song_id = int(song_id)
            # 限制song_id的范围，确保不会超出MySQL BIGINT类型的范围
            if song_id < -9223372036854775808 or song_id > 9223372036854775807:
                return jsonify({'message': '歌曲ID超出有效范围'}), 400
        except ValueError:
            return jsonify({'message': '歌曲ID格式错误'}), 400
        
        # 保存到数据库
        with Mysql() as mysql:
            # 先检查是否已经存在相同的播放记录
            existing_record = mysql.sql(
                "SELECT id FROM play_history WHERE user_id=%s AND song_id=%s",
                [user_id, song_id]
            )
            
            if isinstance(existing_record, list) and existing_record:
                # 记录已存在，更新播放时间
                result = mysql.sql(
                    "UPDATE play_history SET play_time=CURRENT_TIMESTAMP WHERE user_id=%s AND song_id=%s",
                    [user_id, song_id]
                )
                action = "更新"
            else:
                # 记录不存在，插入新记录
                result = mysql.sql(
                    "INSERT INTO play_history (user_id, song_id) VALUES (%s, %s)",
                    [user_id, song_id]
                )
                action = "插入"
            
            # 检查操作是否成功，先确保result不为None
            if result is None:
                return jsonify({'message': '播放历史保存失败'}), 500
            
            # 检查操作是否成功
            if (isinstance(result, tuple) and result[0] and result[0] > 0) or \
               (isinstance(result, int) and result > 0):
                current_app.logger.info(f"用户 {user_id} 播放历史{action}成功: 歌曲ID {song_id}")
                return jsonify({'message': '播放历史保存成功'}), 200
            else:
                return jsonify({'message': '播放历史保存失败'}), 500
                
    except Exception as e:
        current_app.logger.error(f"保存播放历史错误: {str(e)}")
        return jsonify({'message': '系统错误，请稍后重试'}), 500

# 获取播放历史接口
@user.route('/get_history', methods=['GET'])
@login_required
def get_play_history():
    """
    获取用户播放历史
    支持分页参数，默认每页10条记录
    """
    try:
        # 获取用户ID
        user_id = session.get('user_id')
        
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 从数据库获取播放历史，按播放时间倒序排列
        with Mysql() as mysql:
            # 获取总记录数
            total_count = mysql.sql(
                "SELECT COUNT(*) as count FROM play_history WHERE user_id = %s",
                [user_id]
            )
            total = total_count[0]['count'] if total_count else 0
            
            # 获取分页数据
            history_list = mysql.sql(
                """
                SELECT song_id, play_time 
                FROM play_history 
                WHERE user_id = %s 
                ORDER BY play_time DESC 
                LIMIT %s OFFSET %s
                """,
                [user_id, page_size, offset]
            )
            
            # 去重处理，保留最新的播放记录
            unique_songs = {}
            for record in history_list:
                if record['song_id'] not in unique_songs:
                    unique_songs[record['song_id']] = record
            
            # 转换为列表
            unique_history = list(unique_songs.values())
            
            # 批量获取歌曲详情
            song_ids = [record['song_id'] for record in unique_history]
            enriched_history = []
            
            try:
                # 使用批量获取歌曲详情的方式，减少API调用次数
                # 每50首歌一批进行处理
                song_details_map = {}
                for i in range(0, len(song_ids), 50):
                    batch_ids = song_ids[i:i+50]
                    
                    # 使用批量获取函数
                    batch_result = get_songs_detail(batch_ids)
                    
                    # 处理批量结果
                    if batch_result and batch_result.get('code') == 200 and 'songs' in batch_result:
                        for song in batch_result['songs']:
                            if song and 'id' in song:
                                song_details_map[song['id']] = song
                
                # 构建丰富的历史记录列表
                for record in unique_history:
                    song_id = record['song_id']
                    try:
                        if song_id in song_details_map:
                            song = song_details_map[song_id]
                            # 丰富历史记录数据
                            enriched_record = {
                                'song_id': song_id,
                                'play_time': record['play_time'],
                                'name': song.get('name', '未知歌曲'),
                                'artist': '/'.join([ar.get('name', '') for ar in song.get('ar', []) if ar.get('name')]),
                                'cover_url': song.get('al', {}).get('picUrl', ''),
                                'album': song.get('al', {}).get('name', '未知专辑')
                            }
                            enriched_history.append(enriched_record)
                        else:
                            # 获取失败，使用基本信息
                            enriched_history.append({
                                'song_id': song_id,
                                'play_time': record['play_time'],
                                'name': f'歌曲ID: {song_id}',
                                'artist': '未知歌手',
                                'cover_url': '',
                                'album': '未知专辑'
                            })
                    except Exception as e:
                        current_app.logger.error(f"处理歌曲{song_id}详情失败: {str(e)}")
                        # 失败时仍然添加基本信息
                        enriched_history.append({
                            'song_id': song_id,
                            'play_time': record['play_time'],
                            'name': f'歌曲ID: {song_id}',
                            'artist': '未知歌手',
                            'cover_url': '',
                            'album': '未知专辑'
                        })
            except Exception as e:
                current_app.logger.error(f"批量获取歌曲详情失败: {str(e)}")
                # 如果批量获取失败，返回原始数据
                enriched_history = unique_history
            
            # 计算总页数
            total_pages = (total + page_size - 1) // page_size
            
            # 构造响应数据
            data = {
                'history': enriched_history,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages,
                'has_details': len(enriched_history) > 0 and 'name' in enriched_history[0]
            }
            
            current_app.logger.info(f"用户 {user_id} 获取播放历史成功: 第{page}页，共{total_pages}页")
            return jsonify(data), 200
            
    except Exception as e:
        current_app.logger.error(f"获取播放历史错误: {str(e)}")
        return jsonify({'message': '系统错误，请稍后重试'}), 500


# 修改用户名称接口
@user.route('/update_username', methods=['POST'])
@login_required
def update_username():
    """
    修改用户名称
    POST参数: new_username (新的用户名)
    """
    try:
        user_id = session.get('user_id')
        
        # 获取并验证新用户名
        # 先尝试获取表单数据，如果没有再尝试获取JSON数据
        data = dict(request.form)
        if not data:
            data = request.get_json(silent=True, force=True) or {}
        new_username = data.get('new_username', '').strip()
        
        # 验证新用户名格式
        if not new_username:
            return jsonify({'message': '用户名不能为空'}), 400
            
        # 使用现有的验证函数检查用户名格式
        # 这里只验证用户名，所以密码参数传入None
        error = validate_user_input(new_username, None)
        if error:
            return jsonify({'message': error}), 400
        
        with Mysql() as mysql:
            # 检查新用户名是否已被其他用户使用
            existing_user = mysql.sql(
                "SELECT id FROM user WHERE username=%s AND deleted=0 AND status=0 AND id!=%s",
                [new_username, user_id]
            )
            
            if isinstance(existing_user, list) and len(existing_user) > 0:
                return jsonify({'message': '用户名已存在'}), 400
            
            # 更新用户名称
            result = mysql.sql(
                "UPDATE user SET username=%s, update_time=CURRENT_TIMESTAMP WHERE id=%s",
                [new_username, user_id]
            )
            
            if isinstance(result, tuple) and len(result) > 0 and result[0] > 0:
                # 更新会话中的用户名
                session['username'] = new_username
                current_app.logger.info(f"用户 {user_id} 修改用户名成功: {new_username}")
                return jsonify({'message': '用户名修改成功'}), 200
            else:
                return jsonify({'message': '用户名修改失败'}), 500
                
    except Exception as e:
        current_app.logger.error(f"修改用户名错误: {str(e)}")
        return jsonify({'message': '系统错误，请稍后重试'}), 500


# 修改用户密码接口
@user.route('/update_password', methods=['POST'])
@login_required
def update_password():
    """
    修改用户密码
    POST参数: old_password (原密码), new_password (新密码), confirm_password (确认新密码)
    """
    try:
        user_id = session.get('user_id')
        
        # 获取并验证密码信息
        # 先尝试获取表单数据，如果没有再尝试获取JSON数据
        data = dict(request.form)
        if not data:
            data = request.get_json(silent=True, force=True) or {}
        old_password = data.get('old_password', data.get('current_password', '')).strip()
        new_password = data.get('new_password', '').strip()
        confirm_password = data.get('confirm_password', '').strip()
        
        # 验证密码格式
        error = validate_user_input('', new_password, confirm_password)
        if error:
            return jsonify({'message': error}), 400
        
        # 检查原密码是否正确
        hashed_old_password = hashlib.sha256(old_password.encode()).hexdigest()
        
        with Mysql() as mysql:
            # 验证原密码
            user = mysql.sql(
                "SELECT id FROM user WHERE id=%s AND password=%s AND deleted=0 AND status=0",
                [user_id, hashed_old_password]
            )
            
            if not (isinstance(user, list) and len(user) > 0):
                return jsonify({'message': '原密码错误'}), 400
            
            # 更新密码
            hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
            result = mysql.sql(
                "UPDATE user SET password=%s, update_time=CURRENT_TIMESTAMP WHERE id=%s",
                [hashed_new_password, user_id]
            )
            
            if isinstance(result, tuple) and len(result) > 0 and result[0] > 0:
                current_app.logger.info(f"用户 {user_id} 修改密码成功")
                return jsonify({'message': '密码修改成功'}), 200
            else:
                return jsonify({'message': '密码修改失败'}), 500
    except Exception as e:
        current_app.logger.error(f"修改密码错误: {str(e)}")
        return jsonify({'message': '系统错误，请稍后重试'}), 500


# 同时修改用户名和密码接口
@user.route('/update_account_info', methods=['POST'])
@login_required
def update_account_info():
    """
    同时修改用户名和密码
    POST参数: new_username (新用户名), current_password (当前密码), new_password (新密码)
    """
    try:
        user_id = session.get('user_id')
        
        # 获取并验证所有信息
        # 先尝试获取表单数据，如果没有再尝试获取JSON数据
        data = dict(request.form)
        if not data:
            data = request.get_json(silent=True, force=True) or {}
        new_username = data.get('new_username', '').strip()
        current_password = data.get('current_password', '').strip()
        new_password = data.get('new_password', '').strip()
        
        # 验证所有字段
        if not new_username:
            return jsonify({'message': '用户名不能为空'}), 400
        
        if not current_password:
            return jsonify({'message': '当前密码不能为空'}), 400
        
        if not new_password:
            return jsonify({'message': '新密码不能为空'}), 400
        
        # 验证用户名和密码格式
        error = validate_user_input(new_username, new_password)
        if error:
            return jsonify({'message': error}), 400
        
        with Mysql() as mysql:
            # 检查当前密码是否正确
            hashed_current_password = hashlib.sha256(current_password.encode()).hexdigest()
            user = mysql.sql(
                "SELECT id FROM user WHERE id=%s AND password=%s AND deleted=0 AND status=0",
                [user_id, hashed_current_password]
            )
            
            if not (isinstance(user, list) and len(user) > 0):
                return jsonify({'message': '当前密码错误'}), 400
            
            # 检查新用户名是否已被其他用户使用
            existing_user = mysql.sql(
                "SELECT id FROM user WHERE username=%s AND deleted=0 AND status=0 AND id!=%s",
                [new_username, user_id]
            )
            
            if isinstance(existing_user, list) and len(existing_user) > 0:
                return jsonify({'message': '用户名已存在'}), 400
            
            # 同时更新用户名和密码
            hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
            result = mysql.sql(
                "UPDATE user SET username=%s, password=%s, update_time=CURRENT_TIMESTAMP WHERE id=%s",
                [new_username, hashed_new_password, user_id]
            )
            
            if isinstance(result, tuple) and len(result) > 0 and result[0] > 0:
                # 更新会话中的用户名
                session['username'] = new_username
                current_app.logger.info(f"用户 {user_id} 同时修改用户名和密码成功: {new_username}")
                return jsonify({'message': '账户信息修改成功'}), 200
            else:
                return jsonify({'message': '账户信息修改失败'}), 500
    except Exception as e:
        current_app.logger.error(f"修改账户信息错误: {str(e)}")
        return jsonify({'message': '系统错误，请稍后重试'}), 500


# 修改网易云用户ID接口
@user.route('/update_netease_user_id', methods=['POST'])
@login_required
def update_netease_user_id():
    """
    修改网易云用户ID
    POST参数: new_netease_user_id (新的网易云用户ID)
    """
    try:
        user_id = session.get('user_id')
        
        # 获取并验证新的网易云用户ID
        # 先尝试获取表单数据，如果没有再尝试获取JSON数据
        data = dict(request.form)
        if not data:
            data = request.get_json(silent=True, force=True) or {}
        new_netease_user_id = data.get('new_netease_user_id', '')
        
        # 验证参数
        if new_netease_user_id is None or new_netease_user_id == '':
            # 允许设置为空值
            netease_user_id_value = None
        else:
            try:
                # 尝试将参数转换为整数
                netease_user_id_value = int(new_netease_user_id)
                # 验证是否在BIGINT范围内
                if netease_user_id_value < -9223372036854775808 or netease_user_id_value > 9223372036854775807:
                    return jsonify({'message': '网易云用户ID超出有效范围'}), 400
            except ValueError:
                return jsonify({'message': '网易云用户ID格式错误，必须是整数'}), 400
        
        with Mysql() as mysql:
            # 更新网易云用户ID
            result = mysql.sql(
                "UPDATE user SET netease_user_id=%s, update_time=CURRENT_TIMESTAMP WHERE id=%s",
                [netease_user_id_value, user_id]
            )
            
            # 检查更新是否成功，Mysql.update返回 (count, rowid)
            if isinstance(result, tuple) and len(result) > 0 and result[0] > 0:
                # 同步更新session中的netease_user_id
                session['netease_user_id'] = netease_user_id_value
                current_app.logger.info(f"用户 {user_id} 修改网易云用户ID成功: {netease_user_id_value}")
                return jsonify({'message': '网易云用户ID修改成功'}), 200
            else:
                return jsonify({'message': '网易云用户ID修改失败'}), 500
                
    except Exception as e:
        current_app.logger.error(f"修改网易云用户ID错误: {str(e)}")
        return jsonify({'message': '系统错误，请稍后重试'}), 500


# 获取用户信息接口
@user.route('/get_user_info', methods=['GET'])
@login_required
def get_user_info():
    """
    获取用户信息
    """
    try:
        user_id = session.get('user_id')
        
        with Mysql() as mysql:
            # 获取用户信息
            select_sql = f"SELECT id, username, netease_user_id, status, is_admin FROM user WHERE id = {user_id} AND deleted = 0"
            user_list = mysql.sql(select_sql)
            if not user_list:
                return jsonify({'message': '用户不存在'}), 404

            return jsonify({
                'message': '获取用户信息成功',
                'data': {
                    'id': user_list[0]['id'],
                    'username': user_list[0]['username'],
                    'netease_user_id': user_list[0]['netease_user_id'],
                    'status': user_list[0]['status'],
                    'is_admin': user_list[0]['is_admin']
                }
            }), 200
                
    except Exception as e:
        current_app.logger.error(f"获取用户信息错误: {str(e)}")
        return jsonify({'message': '系统错误，请稍后重试'}), 500


# 管理员接口：获取所有用户列表
@user.route('/admin/users', methods=['GET'])
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
                'message': '获取用户列表成功',
                'data': users
            }), 200
    except Exception as e:
        current_app.logger.error(f"获取用户列表错误: {str(e)}")
        return jsonify({'message': '系统错误，请稍后重试'}), 500


# 管理员接口：删除用户
@user.route('/admin/users/<int:target_user_id>', methods=['DELETE'])
@admin_required
def delete_user(target_user_id):
    """
    管理员删除用户
    """
    try:
        # 防止删除自己
        current_user_id = session.get('user_id')
        if current_user_id == target_user_id:
            return jsonify({'message': '不能删除自己'}), 400
            
        with Mysql() as mysql:
            # 检查用户是否存在
            select_sql = f"SELECT id FROM user WHERE id = {target_user_id} AND deleted = 0"
            user = mysql.sql(select_sql)
            if not user:
                return jsonify({'message': '用户不存在'}), 404
            
            # 逻辑删除用户
            delete_sql = f"UPDATE user SET deleted = 1 WHERE id = {target_user_id}"
            result = mysql.sql(delete_sql)
            
            # 删除用户的所有歌单
            delete_playlists_sql = f"UPDATE playlist SET deleted = 1 WHERE user_id = {target_user_id}"
            mysql.sql(delete_playlists_sql)
            
            return jsonify({'message': '删除用户成功'}), 200
    except Exception as e:
        current_app.logger.error(f"删除用户错误: {str(e)}")
        return jsonify({'message': '系统错误，请稍后重试'}), 500


# 管理员接口：封禁用户
@user.route('/admin/users/<int:target_user_id>/ban', methods=['PUT'])
@admin_required
def ban_user(target_user_id):
    """
    管理员封禁用户
    """
    try:
        # 防止封禁自己
        current_user_id = session.get('user_id')
        if current_user_id == target_user_id:
            return jsonify({'message': '不能封禁自己'}), 400
            
        with Mysql() as mysql:
            # 检查用户是否存在
            select_sql = f"SELECT id FROM user WHERE id = {target_user_id} AND deleted = 0"
            user = mysql.sql(select_sql)
            if not user:
                return jsonify({'message': '用户不存在'}), 404
            
            # 封禁用户
            ban_sql = f"UPDATE user SET status = 0 WHERE id = {target_user_id}"
            result = mysql.sql(ban_sql)
            
            return jsonify({'message': '封禁用户成功'}), 200
    except Exception as e:
        current_app.logger.error(f"封禁用户错误: {str(e)}")
        return jsonify({'message': '系统错误，请稍后重试'}), 500


# 管理员接口：解放用户
@user.route('/admin/users/<int:target_user_id>/unban', methods=['PUT'])
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
                return jsonify({'message': '用户不存在'}), 404
            
            # 解放用户
            unban_sql = f"UPDATE user SET status = 1 WHERE id = {target_user_id}"
            result = mysql.sql(unban_sql)
            
            return jsonify({'message': '解放用户成功'}), 200
    except Exception as e:
        current_app.logger.error(f"解放用户错误: {str(e)}")
        return jsonify({'message': '系统错误，请稍后重试'}), 500


# 管理员接口：设置用户为管理员
@user.route('/admin/users/<int:target_user_id>/set_admin', methods=['PUT'])
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
                return jsonify({'message': '用户不存在'}), 404
            
            # 设置为管理员
            set_admin_sql = f"UPDATE user SET is_admin = 1 WHERE id = {target_user_id}"
            result = mysql.sql(set_admin_sql)
            
            return jsonify({'message': '设置用户为管理员成功'}), 200
    except Exception as e:
        current_app.logger.error(f"设置用户为管理员错误: {str(e)}")
        return jsonify({'message': '系统错误，请稍后重试'}), 500


# 管理员接口：修改用户信息
@user.route('/admin/users/<int:target_user_id>', methods=['PUT'])
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
            return jsonify({'message': '请至少提供一个需要修改的字段'}), 400
        
        with Mysql() as mysql:
            # 检查用户是否存在
            user = mysql.sql(f"SELECT id, username FROM user WHERE id = {target_user_id} AND deleted = 0")
            if not user:
                return jsonify({'message': '用户不存在'}), 404
            
            # 构建更新语句
            update_fields = []
            update_values = []
            
            if username:
                username = username.strip()
                if not username:
                    return jsonify({'message': '用户名不能为空'}), 400
                    
                # 检查用户名是否已存在
                existing_user = mysql.sql(
                    "SELECT id FROM user WHERE username=%s AND deleted=0 AND status=0 AND id!=%s",
                    [username, target_user_id]
                )
                if existing_user:
                    return jsonify({'message': '用户名已存在'}), 400
                    
                update_fields.append("username = %s")
                update_values.append(username)
            
            if password:
                password = password.strip()
                if not password:
                    return jsonify({'message': '密码不能为空'}), 400
                    
                # 验证密码格式
                error = validate_user_input('', password)
                if error:
                    return jsonify({'message': error}), 400
                    
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
                return jsonify({'message': '修改用户信息成功'}), 200
            else:
                return jsonify({'message': '没有可更新的字段'}), 400
                
    except Exception as e:
        current_app.logger.error(f"管理员修改用户信息错误: {str(e)}")
        return jsonify({'message': '系统错误，请稍后重试'}), 500


# 管理员接口：获取所有歌单
@user.route('/admin/playlists', methods=['GET'])
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
                'playlists': playlists,
                'total': len(playlists)
            }), 200
            
    except Exception as e:
        current_app.logger.error(f"管理员获取所有歌单错误: {str(e)}")
        return jsonify({'message': '系统错误，请稍后重试'}), 500


# 管理员接口：根据用户ID获取歌单
@user.route('/admin/users/<int:user_id>/playlists', methods=['GET'])
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
                return jsonify({'message': '用户不存在'}), 404
            
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
                'user': user[0],
                'playlists': playlists,
                'total': len(playlists)
            }), 200
            
    except Exception as e:
        current_app.logger.error(f"管理员获取用户歌单错误: {str(e)}")
        return jsonify({'message': '系统错误，请稍后重试'}), 500
