from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify, current_app
from apps.tool.Mysql import Mysql
import hashlib
from functools import wraps
from apps.music import get_song_detail


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)

    return decorated_function


user = Blueprint('user', __name__, url_prefix='/user')


def validate_user_input(username, password, confirm_password=None):
    """验证用户输入"""
    if not username or not password:
        return '用户名和密码不能为空'

    if len(username) < 3 or len(username) > 20:
        return '用户名长度应在3-20个字符之间'

    if len(password) < 6 or len(password) > 20:
        return '密码长度应在6-20个字符之间'

    if confirm_password and password != confirm_password:
        return '两次输入的密码不一致'

    return None


@user.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
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
                # 使用参数化查询防止SQL注入
                user_list = mysql.sql(
                    "SELECT id, username FROM tabl_user WHERE username=%s AND password=%s",
                    [username, hashed_password]
                )

                # 检查返回结果是否为列表且不为空
                if isinstance(user_list, list) and len(user_list) > 0:
                    # 设置用户会话
                    current_app.logger.info(f"用户登录成功: {username}")
                    session['user_id'] = user_list[0]['id']
                    session['username'] = user_list[0]['username']
                    return jsonify({'message': '登录成功'}), 200
                else:
                    current_app.logger.warning(f"用户登录失败 - 账号密码错误: {username}")
                    return jsonify({'message': '账号密码错误'}), 401

        except Exception as e:
            # 记录详细错误日志
            current_app.logger.error(f"登录错误: {str(e)}")
            return jsonify({'message': '系统错误，请稍后重试'}), 500

    # GET请求显示登录页面
    return render_template('user/login.html')


@user.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
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
                # 检查用户名是否已存在
                existing_user = mysql.sql(
                    "SELECT id FROM tabl_user WHERE username=%s",
                    [username]
                )

                if isinstance(existing_user, list) and len(existing_user) > 0:
                    return jsonify({'message': '用户名已存在'}), 400

                # 插入新用户
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                result = mysql.sql(
                    "INSERT INTO tabl_user (username, password) VALUES (%s, %s)",
                    [username, hashed_password]
                )

                if isinstance(result, tuple) and result[0] > 0:
                    return jsonify({'message': '注册成功，请登录'}), 200
                else:
                    return jsonify({'message': '注册失败，请重试'}), 500

        except Exception as e:
            current_app.logger.error(f"注册错误: {str(e)}")
            return jsonify({'message': '系统错误，请稍后重试'}), 500

    # GET请求显示注册页面
    return render_template('user/register.html')


@user.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('user.login'))


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
            # 检查用户是否已存在同名歌单
            existing = mysql.sql(
                "SELECT id FROM playlist WHERE user_id = %s AND name = %s",
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


@user.route('/playlists', methods=['GET'])
@login_required
def get_playlists():
    """
    获取用户的所有歌单列表
    """
    try:
        user_id = session.get('user_id')
        
        with Mysql() as mysql:
            # 查询用户的所有歌单
            playlists = mysql.sql(
                """
                SELECT p.id, p.name, p.cover_url, p.description, p.create_time, p.update_time,
                       COUNT(ps.song_id) as song_count
                FROM playlist p
                LEFT JOIN playlist_song ps ON p.id = ps.playlist_id
                WHERE p.user_id = %s
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


@user.route('/playlist_detail', methods=['GET'])
@login_required
def playlist_detail_page():
    """
    歌单详情页面路由 - 重定向到首页，由前端通过动态加载显示
    GET参数: id (歌单ID)
    """
    from flask import redirect, url_for
    # 重定向到首页，前端会根据需要动态加载歌单详情
    return redirect(url_for('index'))


@user.route('/playlist/<int:playlist_id>', methods=['GET'])
@login_required
def get_playlist_detail(playlist_id):
    """
    获取歌单详情，包括歌单中的歌曲
    """
    try:
        user_id = session.get('user_id')
        
        with Mysql() as mysql:
            # 首先检查歌单是否存在且属于当前用户
            playlist = mysql.sql(
                "SELECT id, name, cover_url, description, create_time, update_time FROM playlist WHERE id = %s AND user_id = %s",
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
            
            # 批量获取歌曲详情
            enriched_songs = []
            try:
                for song_info in songs:
                    song_id = song_info['song_id']
                    try:
                        # 获取歌曲详情
                        detail = get_song_detail(song_id)
                        if detail.get('code') == 200 and detail.get('songs'):
                            song = detail['songs'][0]
                            enriched_song = {
                                'song_id': song_id,
                                'add_time': song_info['add_time'],
                                'name': song.get('name', '未知歌曲'),
                                'artist': '/'.join([ar.get('name', '') for ar in song.get('ar', []) if ar.get('name')]),
                                'cover_url': song.get('al', {}).get('picUrl', ''),
                                'album': song.get('al', {}).get('name', '未知专辑')
                            }
                            enriched_songs.append(enriched_song)
                        else:
                            # 获取失败，使用基本信息
                            enriched_songs.append({
                                'song_id': song_id,
                                'add_time': song_info['add_time'],
                                'name': f'歌曲ID: {song_id}',
                                'artist': '未知歌手',
                                'cover_url': '',
                                'album': '未知专辑'
                            })
                    except Exception as e:
                        current_app.logger.error(f"获取歌曲{song_id}详情失败: {str(e)}")
                        # 失败时仍然添加基本信息
                        enriched_songs.append({
                            'song_id': song_id,
                            'add_time': song_info['add_time'],
                            'name': f'歌曲ID: {song_id}',
                            'artist': '未知歌手',
                            'cover_url': '',
                            'album': '未知专辑'
                        })
            except Exception as e:
                current_app.logger.error(f"批量获取歌曲详情失败: {str(e)}")
                enriched_songs = songs
            
            current_app.logger.info(f"用户 {user_id} 获取歌单详情成功: ID {playlist_id}")
            return jsonify({
                'playlist': playlist[0],
                'songs': enriched_songs,
                'song_count': len(enriched_songs)
            }), 200
            
    except Exception as e:
        current_app.logger.error(f"获取歌单详情错误: {str(e)}")
        return jsonify({'message': '系统错误，请稍后重试'}), 500


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
            # 首先检查歌单是否存在且属于当前用户
            playlist = mysql.sql(
                "SELECT id FROM playlist WHERE id = %s AND user_id = %s",
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
            # 首先检查歌单是否存在且属于当前用户
            playlist = mysql.sql(
                "SELECT id FROM playlist WHERE id = %s AND user_id = %s",
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
            # 首先检查歌单是否存在且属于当前用户
            playlist = mysql.sql(
                "SELECT id FROM playlist WHERE id = %s AND user_id = %s",
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
            # 首先检查歌单是否存在且属于当前用户
            playlist = mysql.sql(
                "SELECT id, name FROM playlist WHERE id = %s AND user_id = %s",
                [playlist_id, user_id]
            )
            
            if not (isinstance(playlist, list) and playlist):
                return jsonify({'message': '歌单不存在或无权访问'}), 404
            
            playlist_name = playlist[0].get('name', '')
            
            # 级联删除：先删除歌单中的所有歌曲记录
            mysql.sql(
                "DELETE FROM playlist_song WHERE playlist_id = %s",
                [playlist_id]
            )
            
            # 删除歌单本身
            playlist_delete_result = mysql.sql(
                "DELETE FROM playlist WHERE id = %s AND user_id = %s",
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
                # 每10首歌一批进行处理
                for i in range(0, len(song_ids), 10):
                    batch_ids = song_ids[i:i+10]
                    
                    # 构建批量请求数据
                    songs_data = []
                    for song_id in batch_ids:
                        try:
                            # 获取单首歌曲详情
                            detail = get_song_detail(song_id)
                            if detail.get('code') == 200 and detail.get('songs'):
                                song = detail['songs'][0]
                                # 找到对应的历史记录
                                history_record = next((r for r in unique_history if r['song_id'] == song_id), None)
                                if history_record:
                                    # 丰富历史记录数据
                                    enriched_record = {
                                        'song_id': song_id,
                                        'play_time': history_record['play_time'],
                                        'name': song.get('name', '未知歌曲'),
                                        'artist': '/'.join([ar.get('name', '') for ar in song.get('ar', []) if ar.get('name')]),
                                        'cover_url': song.get('al', {}).get('picUrl', ''),
                                        'album': song.get('al', {}).get('name', '未知专辑')
                                    }
                                    enriched_history.append(enriched_record)
                            else:
                                # 获取失败，使用基本信息
                                history_record = next((r for r in unique_history if r['song_id'] == song_id), None)
                                if history_record:
                                    enriched_history.append({
                                        'song_id': song_id,
                                        'play_time': history_record['play_time'],
                                        'name': f'歌曲ID: {song_id}',
                                        'artist': '未知歌手',
                                        'cover_url': '',
                                        'album': '未知专辑'
                                    })
                        except Exception as e:
                            current_app.logger.error(f"获取歌曲{song_id}详情失败: {str(e)}")
                            # 失败时仍然添加基本信息
                            history_record = next((r for r in unique_history if r['song_id'] == song_id), None)
                            if history_record:
                                enriched_history.append({
                                    'song_id': song_id,
                                    'play_time': history_record['play_time'],
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
