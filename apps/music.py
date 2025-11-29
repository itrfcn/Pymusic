import json
import urllib.parse
from hashlib import md5
from random import randrange
from typing import Dict, List, Union
from dataclasses import dataclass
import requests
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from flask import Blueprint, request, jsonify, redirect, Response, current_app
from config import current_config

# ========== 全局配置 ==========
music = Blueprint('music', __name__, url_prefix="/music")
AES_KEY = getattr(current_config, 'NETEASE_MUSIC_AES_KEY', b"e82ckenh8dichen8")
MUSIC_LEVEL_MAP = {
    'standard': "标准音质",
    'exhigh': "极高音质",
    'lossless': "无损音质",
    'hires': "Hires音质",
    'sky': "沉浸环绕环绕声",
    'jyeffect': "高清环绕声",
    'jymaster': "超清母带"
}
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Chrome/91.0.4472.164 NeteaseMusicDesktop/2.10.2.200154',
    'Referer': '',
}
WEB_HEADERS = {
    # 模拟网易云音乐桌面版客户端的 User-Agent
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Chrome/91.0.4472.164 NeteaseMusicDesktop/2.10.2.200154',
    'Referer': 'https://music.163.com/',
}


# ========== 数据模型 ==========
@dataclass
class SongInfo:
    id: int
    name: str
    pic_url: str
    artist: str
    album: str
    level: str
    size: str
    url: str
    lyric: str
    tlyric: str


# ========== 工具函数 ==========
def hex_digest(data: bytes) -> str:
    return "".join([hex(d)[2:].zfill(2) for d in data])


def hash_digest(text: str) -> bytes:
    return md5(text.encode("utf-8")).digest()


def hash_hex_digest(text: str) -> str:
    return hex_digest(hash_digest(text))


def parse_cookie(text: str) -> Dict[str, str]:
    if not text.strip():
        return {}
    cookie_list = [item.strip().split('=', 1) for item in text.strip().split(';') if item.strip()]
    return {k.strip(): v.strip() for k, v in cookie_list if len(v) >= 1}


def read_cookie() -> str:
    try:
        # 从配置文件中获取cookie
        cookie = current_app.config.get('NETEASE_MUSIC_COOKIE', '')
        if cookie:
            return cookie.strip()
        current_app.logger.warning("配置中未设置NETEASE_MUSIC_COOKIE")
        return ""
    except Exception as e:
        current_app.logger.error(f"读取Cookie配置失败：{str(e)}")
        return ""


def request_post(url: str, params: str, cookie: Dict[str, str]) -> Dict[str, Union[str, int]]:
    headers = DEFAULT_HEADERS.copy()
    cookies = {"os": "pc", "appver": "", "osver": "", "deviceId": "pyncm!"}
    cookies.update(cookie)

    try:
        response = requests.post(
            url, headers=headers, cookies=cookies, data={"params": params}, timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        current_app.logger.error(f"请求超时：{url}")
        return {"code": 504, "message": "请求超时"}
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"请求失败：{url}，错误：{str(e)}")
        return {"code": 500, "message": f"请求失败：{str(e)}"}
    except json.JSONDecodeError:
        current_app.logger.error(f"响应解析失败：{url}")
        return {"code": 500, "message": "响应格式错误"}


def parse_song_id(ids: str) -> str:
    if not ids:
        return ""
    if '163cn.tv' in ids:
        try:
            response = requests.get(ids, allow_redirects=False, timeout=5)
            ids = response.headers.get('Location', ids)
        except requests.RequestException:
            current_app.logger.warning(f"短链接解析失败：{ids}")
    if 'music.163.com' in ids:
        id_start = ids.find('id=')
        if id_start != -1:
            ids = ids[id_start + 3:].split('&')[0]
    return ids.strip()


def format_file_size(size_bytes: int) -> str:
    if size_bytes <= 0:
        return "0B"
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = size_bytes
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    return f"{size:.2f}{units[unit_index]}"


def get_music_level(level: str) -> str:
    return MUSIC_LEVEL_MAP.get(level, "未知音质")


def get_song_url(song_id: Union[str, int], level: str, cookies: Dict[str, str]) -> Dict[str, Union[str, int]]:
    url = "https://interface3.music.163.com/eapi/song/enhance/player/url/v1"
    if not song_id or not level:
        return {"code": 400, "message": "歌曲ID和音质不能为空"}

    config = {
        "os": "pc", "appver": "", "osver": "", "deviceId": "pyncm!",
        "requestId": str(randrange(20000000, 30000000))
    }
    payload = {
        'ids': [str(song_id)], 'level': level, 'encodeType': 'flac',
        'header': json.dumps(config)
    }
    if level == 'sky':
        payload['immerseType'] = 'c51'

    try:
        url_path = urllib.parse.urlparse(url).path.replace("/eapi/", "/api/")
        digest = hash_hex_digest(f"nobody{url_path}use{json.dumps(payload)}md5forencrypt")
        params_str = f"{url_path}-36cd479b6b5-{json.dumps(payload)}-36cd479b6b5-{digest}"

        padder = padding.PKCS7(algorithms.AES(AES_KEY).block_size).padder()
        padded_data = padder.update(params_str.encode('utf-8')) + padder.finalize()
        cipher = Cipher(algorithms.AES(AES_KEY), modes.ECB())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        encrypted_params = hex_digest(encrypted_data)

        return request_post(url, encrypted_params, cookies)
    except Exception as e:
        current_app.logger.error(f"加密失败：{str(e)}")
        return {"code": 500, "message": f"加密失败：{str(e)}"}


def get_song_detail(song_id: Union[str, int]) -> Dict[str, Union[str, int, List]]:
    """获取单个歌曲详情
    
    Args:
        song_id: 歌曲ID
    
    Returns:
        包含歌曲详情的字典
    """
    return get_songs_detail([song_id])

def get_songs_detail(song_ids: List[Union[str, int]]) -> Dict[str, Union[str, int, List]]:
    """批量获取多个歌曲详情
    
    Args:
        song_ids: 歌曲ID列表
    
    Returns:
        包含所有歌曲详情的字典
    """
    url = "https://interface3.music.163.com/api/v3/song/detail"
    try:
        # 构建批量请求数据
        song_list = [{"id": str(song_id), "v": 0} for song_id in song_ids]
        data = {'c': json.dumps(song_list)}
        response = requests.post(url, data=data, headers=WEB_HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        current_app.logger.error(f"批量获取歌曲详情失败，错误：{str(e)}")
        return {"code": 500, "message": f"批量获取详情失败：{str(e)}"}


def get_song_lyric(song_id: Union[str, int], cookies: Dict[str, str]) -> Dict[str, Union[str, int]]:
    url = "https://interface3.music.163.com/api/song/lyric"
    data = {
        'id': str(song_id), 'cp': 'false', 'tv': '0', 'lv': '0', 'rv': '0',
        'kv': '0', 'yv': '0', 'ytv': '0', 'yrv': '0'
    }
    try:
        response = requests.post(
            url, data=data, cookies=cookies, headers=WEB_HEADERS, timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        current_app.logger.error(f"获取歌词失败：{song_id}，错误：{str(e)}")
        return {"code": 500, "message": f"获取歌词失败：{str(e)}"}


# ========== 接口路由 ==========

# 解析接口
@music.route('/jx', methods=['GET', 'POST'])
def song_parse():
    song_ids = request.args.get('ids') or request.form.get('ids')
    url = request.args.get('url') or request.form.get('url')
    level = request.args.get('level') or request.form.get('level')
    type_ = request.args.get('type') or request.form.get('type')

    if not song_ids and not url:
        return jsonify({'error': '必须提供 ids 或 url 参数'}), 400
    if not level:
        return jsonify({'error': 'level参数不能为空'}), 400
    if not type_ or type_ not in ['text', 'down', 'json']:
        return jsonify({'error': 'type参数必须为 text/down/json'}), 400

    target_id = parse_song_id(song_ids) if song_ids else parse_song_id(url)
    if not target_id:
        return jsonify({'error': '无法解析歌曲ID'}), 400

    cookies = parse_cookie(read_cookie())
    url_data = get_song_url(target_id, level, cookies)

    if url_data.get('code') != 200:
        return jsonify({"status": 400, 'msg': url_data.get('message', '获取播放URL失败')}), 400
    data_list = url_data.get('data', [])
    if not data_list or not data_list[0].get('url'):
        return jsonify({"status": 400, 'msg': '信息获取不完整'}), 400

    detail_data = get_song_detail(data_list[0]['id'])
    if detail_data.get('code') != 200:
        return jsonify({"status": 400, 'msg': detail_data.get('message', '获取歌曲详情失败')}), 400
    songs = detail_data.get('songs', [])
    if not songs:
        return jsonify({"status": 400, 'msg': '未找到歌曲信息'}), 400
    song = songs[0]

    lyric_data = get_song_lyric(data_list[0]['id'], cookies)
    lyric = lyric_data.get('lrc', {}).get('lyric', '')
    tlyric = lyric_data.get('tlyric', {}).get('lyric', '')

    song_info = SongInfo(
        id=data_list[0]['id'],
        name=song.get('name', '未知歌曲'),
        pic_url=song.get('al', {}).get('picUrl', ''),
        artist='/'.join([ar.get('name', '') for ar in song.get('ar', []) if ar.get('name')]),
        album=song.get('al', {}).get('name', '未知专辑'),
        level=get_music_level(data_list[0]['level']),
        size=format_file_size(data_list[0]['size']),
        url=data_list[0]['url'],
        lyric=lyric,
        tlyric=tlyric
    )

    if type_ == 'text':
        html = (
            f'歌曲名称：{song_info.name}<br>'
            f'歌曲图片：{song_info.pic_url}<br>'
            f'歌手：{song_info.artist}<br>'
            f'专辑：{song_info.album}<br>'
            f'音质：{song_info.level}<br>'
            f'大小：{song_info.size}<br>'
            f'播放地址：{song_info.url}'
        )
        return Response(html, content_type='text/html; charset=utf-8')
    elif type_ == 'down':
        return redirect(song_info.url)
    elif type_ == 'json':
        return jsonify({
            "status": 200,
            "name": song_info.name,
            "pic": song_info.pic_url,
            "ar_name": song_info.artist,
            "al_name": song_info.album,
            "level": song_info.level,
            "size": song_info.size,
            "url": song_info.url,
            "lyric": song_info.lyric,
            "tlyric": song_info.tlyric
        })

# 搜索接口
@music.route('/search')
def search_song():
    # 从查询参数中获取搜索关键词和页码
    name = request.args.get('name', '', type=str)
    page = request.args.get('page', 0, type=int)
    if page < 0:
        page = 0
    offset = page * 50

    try:
        encoded_name = urllib.parse.quote(name)
        url = f'https://music.163.com/api/search/get?s={encoded_name}&type=1&limit=30&offset={offset}'
        response = requests.get(url, headers=WEB_HEADERS, timeout=10)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        current_app.logger.error(f"搜索失败：关键词={name}，页码={page}，错误={str(e)}")
        return jsonify({"code": 500, "message": f"搜索失败：{str(e)}"}), 500

# 获取歌单详情接口
@music.route('/playlist/<int:sid>')
def get_playlist(sid: int):
    try:
        # 添加更多参数以获取完整歌曲列表
        url = f'https://music.163.com/api/playlist/detail?id={sid}'
        response = requests.get(url, headers=WEB_HEADERS, timeout=10)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        current_app.logger.error(f"获取歌单失败：ID={sid}，错误={str(e)}")
        return jsonify({
            "code": 500,
            "message": f"获取歌单失败：{str(e)}"
        }), 500

# 获取网易云用户歌单接口
@music.route('/userlist/<int:uid>')
def userlist(uid: int):
    try:
        url = f'https://music.163.com/api/user/playlist/?offset=0&limit=100&uid={uid}'
        response = requests.get(url, headers=WEB_HEADERS, timeout=10)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        current_app.logger.error(f"获取用户歌单失败：UID={uid}，错误={str(e)}")
        return jsonify({
            "code": 500,
            "message": f"获取用户歌单失败：{str(e)}"
        }), 500

# 获取歌曲播放URL接口
@music.route('/song/url/<int:song_id>')
def song_url(song_id: int):
    try:
        level = request.args.get('level', 'lossless')
        cookies = parse_cookie(read_cookie())
        url_data = get_song_url(song_id, level, cookies)

        if url_data and url_data.get('data') and url_data['data'][0].get('url'):
            return jsonify({
                "code": 200,
                "data": {
                    "id": url_data['data'][0]['id'],
                    "url": url_data['data'][0]['url'],
                    "br": url_data['data'][0]['br'],
                    "size": url_data['data'][0]['size'],
                    "level": url_data['data'][0]['level'],
                    "encodeType": url_data['data'][0]['encodeType']
                }
            })
        else:
            return jsonify({
                "code": 404,
                "message": "无法获取歌曲URL"
            }), 404
    except Exception as e:
        current_app.logger.error(f"获取歌曲URL接口错误：{str(e)}")
        return jsonify({
            "code": 500,
            "message": f"服务器内部错误: {str(e)}"
        }), 500

# 获取歌曲歌词接口
@music.route('/song/lyric/<int:song_id>')
def song_lyric(song_id: int):
    try:
        cookies = parse_cookie(read_cookie())
        data = get_song_lyric(song_id, cookies)

        lrc_text = data.get('lrc', {}).get('lyric', '') if isinstance(data.get('lrc'), dict) else ''
        tlyric_text = data.get('tlyric', {}).get('lyric', '') if isinstance(data.get('tlyric'), dict) else ''

        if not lrc_text and not tlyric_text:
            return jsonify({
                "code": 404,
                "message": "未找到歌词"
            }), 404

        return jsonify({
            "code": 200,
            "data": {
                "lrc": lrc_text,
                "tlyric": tlyric_text
            }
        })
    except Exception as e:
        current_app.logger.error(f"获取歌词接口错误：{str(e)}")
        return jsonify({
            "code": 500,
            "message": f"服务器内部错误: {str(e)}"
        }), 500

# 获取歌曲封面接口
@music.route('/song/cover/<int:song_id>')
def song_cover(song_id: int):
    try:
        song_info = get_song_detail(song_id)
        if song_info and song_info.get('songs'):
            pic_url = song_info['songs'][0]['al']['picUrl']
            return jsonify({
                "code": 200,
                "data": {"picUrl": pic_url}
            })
        return jsonify({
            "code": 404,
            "data": {"picUrl": "https://picsum.photos/56/56?random=1"}
        })
    except Exception as e:
        current_app.logger.error(f"获取封面接口错误：{str(e)}")
        return jsonify({
            "code": 500,
            "data": {"picUrl": "https://picsum.photos/56/56?random=1"}
        })

# 获取热门歌单接口
@music.route('/hot_playlists')
def hot_playlists():
    try:
        params = {
            'cat': '全部',
            'order': 'hot',
            'limit': 100,
            'offset': 0
        }
        resp = requests.get(
            'https://music.163.com/api/playlist/list',
            params=params,
            headers=WEB_HEADERS,
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        playlists = data.get('result', {}).get('playlists') or data.get('playlists') or []
        return jsonify({
            "code": 200,
            "playlists": playlists
        })
    except Exception as e:
        current_app.logger.error(f"获取热门歌单错误：{str(e)}")
        return jsonify({
            "code": 500,
            "message": f"服务器内部错误: {str(e)}"
        }), 500