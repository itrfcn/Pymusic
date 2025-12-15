# PyMusic - 在线音乐播放平台

## 📖 项目概述

PyMusic是一个基于Flask框架开发的现代化在线音乐播放平台，集成了网易云音乐API，提供完整的音乐播放、用户管理和数据分析功能。该平台采用前后端分离架构，后端使用Flask提供RESTful API，前端使用原生HTML/CSS/JavaScript和Vue.js（管理后台）构建用户界面。

### 项目背景
随着在线音乐服务的普及，越来越多的用户希望能够在一个平台上方便地搜索、播放和管理自己喜欢的音乐。PyMusic旨在为用户提供一个功能完善、界面友好的在线音乐播放平台，同时为开发者提供一个学习Flask和前后端分离架构的优秀示例。

### 设计理念
- **用户体验优先**：简洁直观的界面设计，流畅的音乐播放体验
- **模块化架构**：采用Flask蓝图实现功能模块分离，便于维护和扩展
- **安全性第一**：全面的安全防护措施，包括IP访问限制、SQL注入检测和XSS防护
- **数据驱动决策**：丰富的数据分析功能，帮助管理员了解用户行为和系统性能

### 项目目标
- 提供完整的在线音乐播放解决方案
- 实现用户个性化音乐体验
- 构建可扩展的前后端分离架构
- 提供全面的管理和数据分析功能
- 确保系统安全性和稳定性

## 🌟 项目特色

### 核心功能
- **音乐播放**：集成网易云音乐API，支持歌曲搜索、播放、歌词展示
- **用户系统**：完整的注册、登录、个人信息管理功能
- **用户歌单**：创建、编辑、删除个性化歌单，支持添加/移除歌曲
- **播放历史**：自动记录用户播放历史，支持查看和管理
- **歌单同步**：自动同步网易云音乐创建的歌单到平台
- **播放列表**：创建、编辑、删除个性化播放列表
- **管理后台**：基于Vue的现代化管理界面，支持用户管理和数据统计
- **数据分析**：用户增长、网站访问量等多维度数据统计和可视化

### 技术亮点
- **模块化设计**：使用Flask蓝图实现功能模块分离，便于扩展和维护
- **安全防护**：IP访问频率限制、SQL注入检测、XSS防护等多重安全机制
- **响应式布局**：适配不同设备屏幕，提供一致的用户体验
- **数据持久化**：MySQL数据库存储用户数据和播放记录，确保数据安全
- **环境配置**：支持.env文件配置多环境（开发、测试、生产）
- **日志系统**：完整的日志记录和分析，便于问题排查和系统监控
- **性能优化**：异步任务处理、数据库索引优化，提升系统性能
- **可视化分析**：使用图表库展示用户增长趋势、播放统计等数据
- **数据清理**：定时清理过期数据，保持数据库清洁和系统性能

## 📁 项目结构

```
wangyi/                     # 项目根目录
├── app.py                    # 应用入口文件，初始化Flask应用和注册蓝图
├── config.py                 # 配置文件，定义应用配置类和环境变量加载
├── requirements.txt          # Python依赖包列表
├── database_schema.sql       # 数据库结构和初始化SQL语句
├── .env.example              # 环境变量示例文件
├── .gitignore                # Git忽略文件配置
├── LICENSE                   # 项目许可证
├── apps/                     # 功能模块目录
│   ├── admin.py              # 管理后台模块，提供管理员功能
│   ├── analytics.py          # 数据分析模块，提供数据统计功能
│   ├── clean_history_data.py # 历史数据清理模块，定时清理过期数据
│   ├── music.py              # 音乐模块，集成网易云音乐API
│   ├── user.py               # 用户模块，提供用户管理功能
│   └── tool/                 # 工具类目录
│       ├── File.py           # 文件操作工具类
│       ├── JS.py             # JavaScript工具类
│       └── Mysql.py          # 数据库操作工具类
├── static/                   # 静态资源目录
│   ├── assets/               # Vue前端打包资源
│   ├── css/                  # 样式文件目录
│   │   └── main.css          # 主要样式文件
│   ├── img/                  # 图片资源目录
│   │   └── logo.png          # 网站Logo
│   └── js/                   # JavaScript文件目录
│       └── main.js           # 主要JavaScript文件
└── templates/                # HTML模板目录
    ├── 404.html              # 404错误页面
    ├── 500.html              # 500错误页面
    ├── admin/                # 管理后台模板
    │   └── index.html        # 管理后台入口页面
    ├── index.html            # 网站首页模板
    ├── partials/             # 部分模板目录
    │   ├── about.html        # 关于页面
    │   ├── discover.html     # 发现音乐页面
    │   ├── doc-163.html      # 网易云文档页面
    │   ├── history.html      # 播放历史页面
    │   └── rank.html         # 排行榜页面
    └── user/                 # 用户页面模板
        ├── edit_profile.html # 编辑个人资料页面
        ├── login.html        # 登录页面
        └── register.html     # 注册页面
```

## 🛠️ 技术栈

### 后端技术
| 技术/框架 | 版本 | 用途 | 选型理由 |
|---------|------|------|---------|
| Python | 3.8+ | 开发语言 | 简单易学、生态丰富、适合Web开发 |
| Flask | 3.0.3 | Web框架 | 轻量级、灵活、易于扩展 |
| PyMySQL | 1.1.2 | MySQL驱动 | 纯Python实现、高性能、稳定 |
| Flask-CORS | 6.0.2 | 跨域资源共享支持 | 解决前后端分离架构中的跨域问题 |
| Flask-Compress | 1.23 | HTTP响应压缩 | 减少响应大小、提高传输速度 |
| Flask-WTF | 1.2.1 | 表单处理和验证 | 简化表单处理、提供CSRF保护 |
| APScheduler | 3.11.1 | 定时任务调度 | 实现定时数据清理、任务调度 |
| python-dotenv | 1.2.1 | 环境变量管理 | 方便管理多环境配置 |

### 前端技术
| 技术/框架 | 版本 | 用途 | 选型理由 |
|---------|------|------|---------|
| HTML5 | - | 页面结构 | 语义化标签、增强的表单控件 |
| CSS3 | - | 页面样式 | 响应式布局、动画效果、渐变 |
| JavaScript (ES6+) | - | 交互逻辑 | 现代JavaScript特性、简洁语法 |
| Vue.js | 3.x | 管理后台框架 | 渐进式框架、组件化开发、响应式数据绑定 |
| art-design-pro | 3.0.0 | 管理后台模板 | 提供响应式布局、组件库、示例代码 |
| Element UI | 3.x | UI组件库 | 美观的组件、完善的文档、易于使用 |

### 数据库
| 数据库 | 版本 | 用途 | 选型理由 |
|-------|------|------|---------|
| MySQL | 5.7+ | 数据存储 | 成熟稳定、高性能、广泛使用 |


## 📋 环境要求

- Python 3.8或更高版本
- MySQL 5.7或更高版本
- pip包管理器（Python 3.4+内置）
- Git版本控制工具
- 现代Web浏览器（Chrome、Firefox、Safari等）

## 🚀 安装部署

### 1. 克隆项目

使用Git克隆项目到本地：

```bash
git clone https://github.com/itrfcn/Pymusic.git
cd Pymusic-main
```



### 2. 创建虚拟环境（推荐）

**Windows系统：**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS系统：**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

在项目根目录下执行以下命令安装Python依赖：

```bash
pip install -r requirements.txt
```

**注意事项**：
- 建议使用虚拟环境（virtualenv或conda）安装依赖，避免与系统Python环境冲突
- 如果安装过程中遇到依赖冲突或其他问题，请参考附录中的"故障排除"部分

### 4. 配置环境变量

复制环境变量示例文件并修改：

```bash
cp .env.example .env
```

使用文本编辑器打开.env文件，配置以下内容：

```env
# Flask配置
FLASK_DEBUG=True
SECRET_KEY=your-secret-key  # 建议使用随机生成的字符串

# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your-password    # 替换为你的MySQL密码
DB_NAME=music

# 服务器配置
HOST=0.0.0.0
PORT=5000

# 网易云音乐API配置
NETEASE_MUSIC_COOKIE=your-netease-cookie  # 必填

# 安全防护配置
IP_RATE_LIMIT_ENABLED=True
IP_RATE_LIMIT=100
IP_RATE_LIMIT_WINDOW=60
SQL_INJECTION_PATTERNS=(union select|select.*from|insert.*into|update.*set|delete.*from|drop table|truncate table)
XSS_PATTERNS=(<script|onload|onerror|onclick|javascript:|alert\()
```

**配置说明**：
- FLASK_DEBUG：设置为True时启用调试模式，便于开发和调试
- SECRET_KEY：用于Flask会话加密，建议使用随机生成的字符串
- DB_*：数据库连接配置，请根据你的MySQL安装情况进行修改
- NETEASE_MUSIC_COOKIE：从网易云音乐网站获取的Cookie
- IP_RATE_LIMIT*：IP访问频率限制配置，防止恶意请求
- SQL_INJECTION_PATTERNS：SQL注入检测模式
- XSS_PATTERNS：XSS攻击检测模式

### 5. 初始化数据库

#### 步骤1：启动MySQL服务

**Windows系统：**
```bash
net start mysql  # 或手动在服务管理中启动MySQL
```

**Linux系统：**
```bash
sudo systemctl start mysql
```

**macOS系统：**
```bash
brew services start mysql
```

#### 步骤2：创建数据库

使用MySQL客户端创建数据库：

```bash
mysql -u root -p -e "CREATE DATABASE music DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

#### 步骤3：导入表结构

执行以下命令导入数据库表结构：

```bash
mysql -u root -p music < database_schema.sql
```
#### 步骤4：添加管理员

默认id为1的管理员为超级管理员

### 6. 启动应用

#### 方法一：本地开发环境部署

在项目根目录下执行以下命令启动应用：

```bash
python app.py
```

应用将在 http://localhost:5000 启动

#### 方法二：生产环境部署

推荐使用Gunicorn或uWSGI部署生产环境：

**使用Gunicorn部署**：
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**使用uWSGI部署**：
```bash
pip install uwsgi
uwsgi --http 0.0.0.0:5000 --wsgi-file app.py --callable app --processes 4 --threads 2
```

**生产环境建议**：
- 使用Nginx作为反向代理服务器
- 配置SSL证书启用HTTPS
- 设置适当的日志级别和日志存储路径
- 定期备份数据库和静态资源


## 🔧 核心功能模块

### 1. 用户模块 (apps/user.py)

用户模块负责处理用户注册、登录、个人信息管理等功能。

```python
# 用户蓝图注册
user = Blueprint('user', __name__, url_prefix='/user')
```

**主要功能**：
- 用户注册/登录/注销
- 个人信息管理（用户名、密码修改）
- 播放历史管理
- 播放列表管理

**核心函数**：
- `login()`：处理用户登录请求，验证用户名和密码
- `register()`：处理用户注册请求，创建新用户
- `get_user_info()`：获取当前登录用户信息
- `update_user_info()`：更新用户个人信息
- `get_play_history()`：获取用户播放历史记录
- `create_playlist()`：创建新的播放列表
- `update_playlist()`：更新播放列表信息
- `delete_playlist()`：删除播放列表

**实现细节**：
- 使用Flask-WTF进行表单验证
- 使用werkzeug.security进行密码加密
- 使用Flask-Login管理用户会话

### 2. 音乐模块 (apps/music.py)

音乐模块负责处理音乐搜索、播放、歌词获取等功能，集成了网易云音乐API。

```python
# 音乐蓝图注册
music = Blueprint('music', __name__, url_prefix="/music")
```

**主要功能**：
- 歌曲搜索
- 歌曲详情获取
- 音乐播放URL获取
- 歌词获取
- 歌单同步

**核心函数**：
- `search()`：搜索歌曲，调用网易云音乐API获取搜索结果
- `detail()`：获取歌曲详情，包括歌曲信息、专辑信息、歌手信息
- `play()`：获取歌曲播放URL，支持多种音质
- `lyric()`：获取歌曲歌词，支持原文和翻译
- `sync_playlist()`：同步网易云歌单到平台

**实现细节**：
- 使用AES加密处理网易云音乐API请求
- 缓存API请求结果，减少重复请求
- 处理API返回数据，转换为前端需要的格式

### 3. 管理模块 (apps/admin.py)

管理模块为管理员提供用户管理、歌单管理和系统设置等功能。

```python
# 管理蓝图注册
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
```

**主要功能**：
- 管理员登录
- 用户管理（查看、编辑、禁用、删除）
- 歌单管理（查看、编辑、删除）
- 系统设置

**核心函数**：
- `admin_login()`：管理员登录，验证管理员账号和密码
- `get_users()`：获取用户列表，支持分页和筛选
- `update_user()`：更新用户信息，包括状态和权限
- `delete_user()`：删除用户，使用软删除机制
- `get_playlists()`：获取歌单列表，支持分页和筛选
- `delete_playlist()`：删除违规歌单

**实现细节**：
- 使用管理员权限装饰器保护管理接口
- 实现用户和歌单的软删除机制
- 支持批量操作和筛选功能

### 4. 数据分析模块 (apps/analytics.py)

数据分析模块提供用户增长、网站访问量等多维度数据统计功能。

```python
# 数据分析蓝图注册
analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')
```

**主要功能**：
- 用户增长分析
- 网站访问量分析
- 播放统计分析

**核心函数**：
- `analyze_user_growth()`：分析用户增长趋势，按日/周/月统计
- `analyze_website_visits()`：分析网站访问量，包括总访问量和每日访问量
- `analyze_play_statistics()`：分析播放统计数据，包括最受欢迎的歌曲和歌手

**实现细节**：
- 读取系统日志文件分析访问量
- 使用数据库查询统计用户和播放数据
- 支持自定义时间范围查询

### 5. 工具类 (apps/tool/)

#### Mysql.py

数据库操作工具类，封装了MySQL数据库的连接和操作方法。

**主要功能**：
- 数据库连接管理
- SQL查询执行
- 事务处理

**核心方法**：
- `__init__()`：初始化数据库连接，加载数据库配置
- `sql()`：执行SQL语句，支持参数化查询
- `select()`：执行查询操作，返回查询结果
- `insert()`：执行插入操作，返回自增ID
- `update()`：执行更新操作，返回影响行数
- `delete()`：执行删除操作，返回影响行数
- `__enter__()`：上下文管理器入口，获取数据库连接
- `__exit__()`：上下文管理器出口，关闭数据库连接

**实现细节**：
- 使用连接池管理数据库连接
- 支持事务处理和异常捕获
- 自动转换查询结果为字典格式

#### File.py

文件操作工具类，提供文件读写、路径处理等功能。

**核心方法**：
- `read_file()`：读取文件内容
- `write_file()`：写入文件内容
- `append_file()`：追加文件内容
- `delete_file()`：删除文件
- `exists()`：检查文件是否存在
- `get_file_size()`：获取文件大小
- `get_file_extension()`：获取文件扩展名

#### JS.py

JavaScript工具类，提供JavaScript代码生成和处理功能。

**核心方法**：
- `generate_js_object()`：生成JavaScript对象
- `generate_js_array()`：生成JavaScript数组
- `escape_js_string()`：转义JavaScript字符串

## 📊 数据库设计

### 数据模型关系图

```
用户表 (user) ←─── 播放历史表 (play_history)
      ↓
播放列表表 (playlist) ←─── 播放列表歌曲表 (playlist_song)
```

### 用户表 (user)

| 字段名 | 类型 | 长度 | 约束 | 描述 | 索引 |
|-------|------|------|------|------|------|
| id | INT | 11 | PRIMARY KEY AUTO_INCREMENT | 用户ID（主键） | 主键索引 |
| username | VARCHAR | 50 | NOT NULL UNIQUE | 用户名（唯一） | 唯一索引 |
| password | VARCHAR | 100 | NOT NULL | 密码（加密存储） | 无 |
| netease_user_id | BIGINT | 20 | NULL | 网易云用户ID | 普通索引 |
| status | TINYINT | 1 | NOT NULL DEFAULT 1 | 用户状态（1:启用，0:禁用） | 普通索引 |
| deleted | TINYINT | 1 | NOT NULL DEFAULT 0 | 是否删除（1:是，0:否） | 普通索引 |
| is_admin | TINYINT | 1 | NOT NULL DEFAULT 0 | 是否管理员（1:是，0:否） | 普通索引 |
| create_time | TIMESTAMP | - | NOT NULL DEFAULT CURRENT_TIMESTAMP | 创建时间 | 普通索引 |
| update_time | TIMESTAMP | - | NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 | 无 |

### 播放历史表 (play_history)

| 字段名 | 类型 | 长度 | 约束 | 描述 | 索引 |
|-------|------|------|------|------|------|
| id | INT | 11 | PRIMARY KEY AUTO_INCREMENT | 记录ID（主键） | 主键索引 |
| user_id | INT | 11 | NOT NULL FOREIGN KEY | 用户ID（外键，关联user.id） | 外键索引 |
| song_id | BIGINT | 20 | NOT NULL | 歌曲ID | 普通索引 |
| song_name | VARCHAR | 200 | NOT NULL | 歌曲名称 | 无 |
| singer_name | VARCHAR | 200 | NOT NULL | 歌手名称 | 无 |
| play_time | DATETIME | - | NOT NULL DEFAULT CURRENT_TIMESTAMP | 播放时间 | 普通索引 |

### 播放列表表 (playlist)

| 字段名 | 类型 | 长度 | 约束 | 描述 | 索引 |
|-------|------|------|------|------|------|
| id | INT | 11 | PRIMARY KEY AUTO_INCREMENT | 列表ID（主键） | 主键索引 |
| user_id | INT | 11 | NOT NULL FOREIGN KEY | 用户ID（外键，关联user.id） | 外键索引 |
| name | VARCHAR | 100 | NOT NULL | 列表名称 | 普通索引 |
| cover_url | LONGTEXT | - | NULL | 封面图片URL | 无 |
| description | TEXT | - | NULL | 描述 | 无 |
| deleted | TINYINT | 1 | NOT NULL DEFAULT 0 | 是否删除（1:是，0:否） | 普通索引 |
| create_time | TIMESTAMP | - | NOT NULL DEFAULT CURRENT_TIMESTAMP | 创建时间 | 无 |
| update_time | TIMESTAMP | - | NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 | 无 |

### 播放列表歌曲表 (playlist_song)

| 字段名 | 类型 | 长度 | 约束 | 描述 | 索引 |
|-------|------|------|------|------|------|
| id | INT | 11 | PRIMARY KEY AUTO_INCREMENT | 记录ID（主键） | 主键索引 |
| playlist_id | INT | 11 | NOT NULL FOREIGN KEY | 播放列表ID（外键，关联playlist.id） | 外键索引 |
| song_id | BIGINT | 20 | NOT NULL | 歌曲ID | 普通索引 |
| song_name | VARCHAR | 200 | NOT NULL | 歌曲名称 | 无 |
| singer_name | VARCHAR | 200 | NOT NULL | 歌手名称 | 无 |
| add_time | TIMESTAMP | - | NOT NULL DEFAULT CURRENT_TIMESTAMP | 添加时间 | 无 |

### 索引优化建议

1. **用户表**：
   - username字段添加唯一索引，提高登录查询效率
   - status和deleted字段添加普通索引，提高用户列表查询效率

2. **播放历史表**：
   - user_id字段添加普通索引，提高用户播放历史查询效率
   - play_time字段添加普通索引，提高按时间查询播放历史效率

3. **播放列表表**：
   - user_id字段添加普通索引，提高用户播放列表查询效率
   - deleted字段添加普通索引，提高播放列表列表查询效率

4. **播放列表歌曲表**：
   - playlist_id字段添加普通索引，提高播放列表歌曲查询效率
   - (playlist_id, song_id)添加联合唯一索引，防止重复添加歌曲

## 🔒 安全防护

### IP访问频率限制

系统实现了基于IP的访问频率限制，防止恶意请求和DDoS攻击。

```python
# IP访问频率限制实现
ip_requests: Dict[str, List[float]] = {}  # 存储IP请求记录

@app.before_request
def ip_rate_limit_middleware():
    if not current_config.IP_RATE_LIMIT_ENABLED:
        return
    
    client_ip = request.remote_addr
    current_time = time.time()
    
    # 清理过期请求记录
    if client_ip in ip_requests:
        ip_requests[client_ip] = [t for t in ip_requests[client_ip] if current_time - t < current_config.IP_RATE_LIMIT_WINDOW]
    else:
        ip_requests[client_ip] = []
    
    # 检查请求数是否超过限制
    if len(ip_requests[client_ip]) >= current_config.IP_RATE_LIMIT:
        return jsonify({
            "code": 429,
            "message": f"IP访问频率过高，请{current_config.IP_RATE_LIMIT_WINDOW}秒后重试"
        }), 429
    
    # 记录当前请求时间
    ip_requests[client_ip].append(current_time)
```

**实现细节**：
- 使用内存存储IP请求记录，生产环境可考虑使用Redis
- 支持自定义时间窗口和请求限制数
- 自动清理过期请求记录，节省内存

### SQL注入检测

系统实现了SQL注入检测功能，防止恶意SQL注入攻击。

```python
# SQL注入检测实现
def detect_sql_injection(content: str) -> bool:
    for pattern in current_config.SQL_INJECTION_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    return False

@app.before_request
def sql_injection_detection_middleware():
    # 检查请求参数
    for param, value in request.args.items():
        if isinstance(value, str) and detect_sql_injection(value):
            return jsonify({
                "code": 403,
                "message": "请求参数包含恶意SQL代码"
            }), 403
    
    # 检查请求体
    if request.is_json:
        try:
            data = request.get_json()
            for key, value in data.items():
                if isinstance(value, str) and detect_sql_injection(value):
                    return jsonify({
                        "code": 403,
                        "message": "请求体包含恶意SQL代码"
                    }), 403
        except Exception:
            pass
```

**实现细节**：
- 使用正则表达式匹配常见的SQL注入模式
- 检查所有请求参数和请求体
- 支持自定义SQL注入检测模式

### XSS防护

系统实现了XSS攻击检测功能，防止跨站脚本攻击。

```python
# XSS防护实现
def detect_xss(content: str) -> bool:
    for pattern in current_config.XSS_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    return False

@app.before_request
def xss_protection_middleware():
    # 检查请求参数
    for param, value in request.args.items():
        if isinstance(value, str) and detect_xss(value):
            return jsonify({
                "code": 403,
                "message": "请求参数包含恶意脚本代码"
            }), 403
    
    # 检查请求体
    if request.is_json:
        try:
            data = request.get_json()
            for key, value in data.items():
                if isinstance(value, str) and detect_xss(value):
                    return jsonify({
                        "code": 403,
                        "message": "请求体包含恶意脚本代码"
                    }), 403
        except Exception:
            pass
```

**实现细节**：
- 使用正则表达式匹配常见的XSS攻击模式
- 检查所有请求参数和请求体
- 支持自定义XSS攻击检测模式

### 其他安全措施

1. **密码加密**：使用werkzeug.security的generate_password_hash函数加密存储密码
2. **CSRF保护**：使用Flask-WTF的CSRF保护功能
3. **HTTPS支持**：生产环境配置SSL证书，启用HTTPS
4. **敏感信息保护**：不在日志中记录敏感信息，如密码、Cookie等
5. **权限控制**：使用装饰器实现接口权限控制

## 📈 数据分析

### 用户增长分析

```python
def analyze_user_growth(start_date=None, end_date=None):
    """
    分析用户增长趋势
    
    Args:
        start_date: 开始日期，格式为YYYY-MM-DD
        end_date: 结束日期，格式为YYYY-MM-DD
    
    Returns:
        dict: 包含日期和新增用户数的字典
    """
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
        
        # 执行查询
        query = f"""
            SELECT DATE(create_time) as date, COUNT(*) as new_users
            FROM user
            WHERE {' AND '.join(where_clause)}
            GROUP BY DATE(create_time)
            ORDER BY date
        """
        result = mysql.sql(query, params)
        
        # 转换结果
        user_growth = {}
        if result is not None:
            for item in result:
                user_growth[str(item['date'])] = item['new_users']
        
        return user_growth
```

**实现细节**：
- 使用数据库查询按日统计新增用户数
- 支持自定义时间范围查询
- 自动处理结果格式转换

### 网站访问量分析

```python
def analyze_website_visits(start_date=None, end_date=None):
    """
    分析网站访问量
    
    Args:
        start_date: 开始日期，格式为YYYY-MM-DD
        end_date: 结束日期，格式为YYYY-MM-DD
    
    Returns:
        dict: 包含总访问量和每日访问量的字典
    """
    # 读取日志文件并分析
    log_file = "app.log"  # 日志文件路径
    daily_visits = {}
    total_visits = 0
    
    if not os.path.exists(log_file):
        return {"total_visits": 0, "daily_visits": {}}
    
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            # 解析日志行，提取日期
            match = re.search(r'\[(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2}\]', line)
            if match:
                date = match.group(1)
                
                # 检查日期范围
                if start_date and date < start_date:
                    continue
                if end_date and date > end_date:
                    continue
                
                # 更新访问量统计
                if date in daily_visits:
                    daily_visits[date] += 1
                else:
                    daily_visits[date] = 1
                total_visits += 1
    
    return {
        "total_visits": total_visits,
        "daily_visits": daily_visits
    }
```

**实现细节**：
- 读取系统日志文件分析访问量
- 使用正则表达式提取日志中的日期信息
- 支持自定义时间范围查询

### 播放统计分析

```python
def analyze_play_statistics(start_date=None, end_date=None):
    """
    分析播放统计数据
    
    Args:
        start_date: 开始日期，格式为YYYY-MM-DD
        end_date: 结束日期，格式为YYYY-MM-DD
    
    Returns:
        dict: 包含播放统计数据的字典
    """
    with Mysql() as mysql:
        # 构建查询条件
        where_clause = []
        params = []
        
        if start_date:
            where_clause.append("DATE(play_time) >= %s")
            params.append(start_date)
        if end_date:
            where_clause.append("DATE(play_time) <= %s")
            params.append(end_date)
        
        # 查询总播放次数
        total_plays_query = f"""
            SELECT COUNT(*) as total_plays
            FROM play_history
            {f'WHERE {" AND ".join(where_clause)}' if where_clause else ''}
        """
        total_plays_result = mysql.sql(total_plays_query, params)
        total_plays = total_plays_result[0]['total_plays'] if total_plays_result else 0
        
        # 查询最受欢迎的歌曲
        popular_songs_query = f"""
            SELECT song_id, song_name, singer_name, COUNT(*) as play_count
            FROM play_history
            {f'WHERE {" AND ".join(where_clause)}' if where_clause else ''}
            GROUP BY song_id, song_name, singer_name
            ORDER BY play_count DESC
            LIMIT 10
        """
        popular_songs_result = mysql.sql(popular_songs_query, params)
        popular_songs = [
            {
                "song_id": song['song_id'],
                "song_name": song['song_name'],
                "singer_name": song['singer_name'],
                "play_count": song['play_count']
            }
            for song in popular_songs_result
        ] if popular_songs_result else []
        
        return {
            "total_plays": total_plays,
            "popular_songs": popular_songs
        }
```

**实现细节**：
- 统计总播放次数和最受欢迎的歌曲
- 支持自定义时间范围查询
- 限制返回最受欢迎的前10首歌曲

## 📝 API文档

### 1. 用户接口

#### 注册接口

- **URL**: `/user/register`
- **方法**: `POST`
- **参数**:
  | 名称 | 类型 | 必需 | 描述 |
  |------|------|------|------|
  | username | string | 是 | 用户名，长度3-20个字符 |
  | password | string | 是 | 密码，长度6-20个字符 |
  | confirm_password | string | 是 | 确认密码，必须与password一致 |

- **响应格式**:
  ```json
  {
    "code": 200,
    "message": "注册成功",
    "data": {
      "user_id": 1,
      "username": "testuser"
    }
  }
  ```

#### 登录接口

- **URL**: `/user/login`
- **方法**: `POST`
- **参数**:
  | 名称 | 类型 | 必需 | 描述 |
  |------|------|------|------|
  | username | string | 是 | 用户名 |
  | password | string | 是 | 密码 |

- **响应格式**:
  ```json
  {
    "code": 200,
    "message": "登录成功",
    "data": {
      "user_id": 1,
      "username": "testuser",
      "is_admin": false
    }
  }
  ```

#### 获取用户信息接口

- **URL**: `/user/info`
- **方法**: `GET`
- **认证**: 需要登录

- **响应格式**:
  ```json
  {
    "code": 200,
    "message": "获取用户信息成功",
    "data": {
      "user_id": 1,
      "username": "testuser",
      "is_admin": false,
      "create_time": "2023-01-01 12:00:00"
    }
  }
  ```

#### 更新用户信息接口

- **URL**: `/user/update`
- **方法**: `POST`
- **认证**: 需要登录
- **参数**:
  | 名称 | 类型 | 必需 | 描述 |
  |------|------|------|------|
  | username | string | 否 | 新用户名，长度3-20个字符 |
  | password | string | 否 | 新密码，长度6-20个字符 |
  | confirm_password | string | 否 | 确认新密码，必须与password一致 |

- **响应格式**:
  ```json
  {
    "code": 200,
    "message": "更新用户信息成功",
    "data": {
      "user_id": 1,
      "username": "newusername"
    }
  }
  ```

### 2. 音乐接口

#### 搜索歌曲接口

- **URL**: `/music/search`
- **方法**: `GET`
- **参数**:
  | 名称 | 类型 | 必需 | 描述 |
  |------|------|------|------|
  | keyword | string | 是 | 搜索关键词 |
  | limit | integer | 否 | 搜索结果数量，默认20 |
  | offset | integer | 否 | 搜索结果偏移量，默认0 |

- **响应格式**:
  ```json
  {
    "code": 200,
    "message": "搜索成功",
    "data": {
      "songs": [
        {
          "id": 123456,
          "name": "歌曲名称",
          "artists": [
            {
              "id": 1001,
              "name": "歌手名称"
            }
          ],
          "album": {
            "id": 2001,
            "name": "专辑名称",
            "picUrl": "https://example.com/album.jpg"
          },
          "duration": 240000
        }
      ],
      "total": 100
    }
  }
  ```

#### 获取歌曲详情接口

- **URL**: `/music/detail`
- **方法**: `GET`
- **参数**:
  | 名称 | 类型 | 必需 | 描述 |
  |------|------|------|------|
  | id | integer | 是 | 歌曲ID |

- **响应格式**:
  ```json
  {
    "code": 200,
    "message": "获取歌曲详情成功",
    "data": {
      "id": 123456,
      "name": "歌曲名称",
      "artists": [
        {
          "id": 1001,
          "name": "歌手名称"
        }
      ],
      "album": {
        "id": 2001,
        "name": "专辑名称",
        "picUrl": "https://example.com/album.jpg"
      },
      "duration": 240000,
      "lyric": "歌曲歌词..."
    }
  }
  ```

#### 播放歌曲接口

- **URL**: `/music/play`
- **方法**: `GET`
- **参数**:
  | 名称 | 类型 | 必需 | 描述 |
  |------|------|------|------|
  | id | integer | 是 | 歌曲ID |
  | quality | string | 否 | 音质，可选值：low, medium, high，默认medium |

- **响应格式**:
  ```json
  {
    "code": 200,
    "message": "获取播放URL成功",
    "data": {
      "url": "https://music.163.com/song/media/outer/url?id=123456.mp3"
    }
  }
  ```

#### 获取歌词接口

- **URL**: `/music/lyric`
- **方法**: `GET`
- **参数**:
  | 名称 | 类型 | 必需 | 描述 |
  |------|------|------|------|
  | id | integer | 是 | 歌曲ID |

- **响应格式**:
  ```json
  {
    "code": 200,
    "message": "获取歌词成功",
    "data": {
      "lyric": "[00:00.00]歌曲名称\n[00:05.00]歌曲歌词...",
      "translated_lyric": "[00:00.00]Song Name\n[00:05.00]Song lyrics..."
    }
  }
  ```

#### 同步歌单接口

- **URL**: `/music/sync-playlist`
- **方法**: `POST`
- **认证**: 需要登录

- **响应格式**:
  ```json
  {
    "code": 200,
    "message": "同步歌单成功",
    "data": {
      "synced_playlists": 3,
      "playlists": [
        {
          "id": 1,
          "name": "我喜欢的音乐",
          "song_count": 100
        }
      ]
    }
  }
  ```

### 3. 管理接口

#### 管理员登录接口

- **URL**: `/admin/login`
- **方法**: `POST`
- **参数**:
  | 名称 | 类型 | 必需 | 描述 |
  |------|------|------|------|
  | username | string | 是 | 管理员用户名 |
  | password | string | 是 | 管理员密码 |

- **响应格式**:
  ```json
  {
    "code": 200,
    "message": "登录成功",
    "data": {
      "user_id": 1,
      "username": "admin",
      "is_admin": true
    }
  }
  ```

#### 获取用户列表接口

- **URL**: `/admin/users`
- **方法**: `GET`
- **认证**: 需要管理员权限
- **参数**:
  | 名称 | 类型 | 必需 | 描述 |
  |------|------|------|------|
  | page | integer | 否 | 页码，默认1 |
  | page_size | integer | 否 | 每页数量，默认20 |
  | username | string | 否 | 用户名搜索关键词 |
  | status | integer | 否 | 用户状态，1:启用，0:禁用 |

- **响应格式**:
  ```json
  {
    "code": 200,
    "message": "获取用户列表成功",
    "data": {
      "users": [
        {
          "id": 1,
          "username": "testuser",
          "is_admin": false,
          "status": 1,
          "create_time": "2023-01-01 12:00:00"
        }
      ],
      "total": 100,
      "page": 1,
      "page_size": 20
    }
  }
  ```

#### 更新用户接口

- **URL**: `/admin/user/update`
- **方法**: `POST`
- **认证**: 需要管理员权限
- **参数**:
  | 名称 | 类型 | 必需 | 描述 |
  |------|------|------|------|
  | user_id | integer | 是 | 用户ID |
  | status | integer | 否 | 用户状态，1:启用，0:禁用 |
  | is_admin | integer | 否 | 是否管理员，1:是，0:否 |

- **响应格式**:
  ```json
  {
    "code": 200,
    "message": "更新用户成功",
    "data": {
      "user_id": 1,
      "status": 0
    }
  }
  ```

#### 删除用户接口

- **URL**: `/admin/user/delete`
- **方法**: `POST`
- **认证**: 需要管理员权限
- **参数**:
  | 名称 | 类型 | 必需 | 描述 |
  |------|------|------|------|
  | user_id | integer | 是 | 用户ID |

- **响应格式**:
  ```json
  {
    "code": 200,
    "message": "删除用户成功"
  }
  ```

### 4. 数据分析接口

#### 用户增长分析接口

- **URL**: `/analytics/user-growth`
- **方法**: `GET`
- **认证**: 需要管理员权限
- **参数**:
  | 名称 | 类型 | 必需 | 描述 |
  |------|------|------|------|
  | start_date | string | 否 | 开始日期，格式YYYY-MM-DD |
  | end_date | string | 否 | 结束日期，格式YYYY-MM-DD |

- **响应格式**:
  ```json
  {
    "code": 200,
    "message": "获取用户增长数据成功",
    "data": {
      "user_growth": {
        "2023-01-01": 10,
        "2023-01-02": 15,
        "2023-01-03": 20
      }
    }
  }
  ```

#### 网站访问量分析接口

- **URL**: `/analytics/website-visits`
- **方法**: `GET`
- **认证**: 需要管理员权限
- **参数**:
  | 名称 | 类型 | 必需 | 描述 |
  |------|------|------|------|
  | start_date | string | 否 | 开始日期，格式YYYY-MM-DD |
  | end_date | string | 否 | 结束日期，格式YYYY-MM-DD |

- **响应格式**:
  ```json
  {
    "code": 200,
    "message": "获取网站访问量数据成功",
    "data": {
      "total_visits": 1000,
      "daily_visits": {
        "2023-01-01": 100,
        "2023-01-02": 150,
        "2023-01-03": 200
      }
    }
  }
  ```

#### 播放统计分析接口

- **URL**: `/analytics/play-statistics`
- **方法**: `GET`
- **认证**: 需要管理员权限
- **参数**:
  | 名称 | 类型 | 必需 | 描述 |
  |------|------|------|------|
  | start_date | string | 否 | 开始日期，格式YYYY-MM-DD |
  | end_date | string | 否 | 结束日期，格式YYYY-MM-DD |

- **响应格式**:
  ```json
  {
    "code": 200,
    "message": "获取播放统计数据成功",
    "data": {
      "total_plays": 5000,
      "popular_songs": [
        {
          "song_id": 123456,
          "song_name": "歌曲名称",
          "singer_name": "歌手名称",
          "play_count": 1000
        }
      ]
    }
  }
  ```

## 🛡️ 环境变量配置

| 变量名 | 类型 | 默认值 | 描述 | 示例值 |
|-------|------|------|------|------|
| FLASK_DEBUG | boolean | True | 是否启用调试模式 | True |
| SECRET_KEY | string | dev-secret-key-for-development | Flask会话加密密钥 | 8a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0 |
| DB_HOST | string | localhost | 数据库主机地址 | 127.0.0.1 |
| DB_PORT | integer | 3306 | 数据库端口 | 3306 |
| DB_USER | string | root | 数据库用户名 | root |
| DB_PASSWORD | string | 123456 | 数据库密码 | my-secret-password |
| DB_NAME | string | music | 数据库名称 | music |
| HOST | string | 0.0.0.0 | 服务器主机地址 | 0.0.0.0 |
| PORT | integer | 5000 | 服务器端口 | 8080 |
| NETEASE_MUSIC_COOKIE | string | - | 网易云音乐Cookie | __remember_me=xxx; MUSIC_U=xxx; |
| IP_RATE_LIMIT_ENABLED | boolean | True | 是否启用IP访问限制 | True |
| IP_RATE_LIMIT | integer | 100 | 每分钟最大请求数 | 200 |
| IP_RATE_LIMIT_WINDOW | integer | 60 | 时间窗口（秒） | 300 |
| SQL_INJECTION_PATTERNS | tuple | (union select|select.*from|insert.*into|update.*set|delete.*from|drop table|truncate table) | SQL注入检测模式 | (union select|select.*from|insert.*into) |
| XSS_PATTERNS | tuple | (<script|onload|onerror|onclick|javascript:|alert\() | XSS攻击检测模式 | (<script|onload|onerror|onclick) |

## 🤝 贡献指南

### 开发环境搭建

1. 克隆项目到本地：`git clone https://github.com/itrfcn/Pymusic.git`
2. 创建虚拟环境：`python -m venv venv`
3. 激活虚拟环境：
   - Windows: `venv\Scripts\activate`
   - Linux/macOS: `source venv/bin/activate`
4. 安装依赖：`pip install -r requirements.txt`
5. 配置环境变量：`cp .env.example .env`
6. 初始化数据库：`mysql -u root -p music < database_schema.sql`
7. 启动应用：`python app.py`

### 代码规范

- 使用PEP 8规范编写Python代码
- 函数和类使用文档字符串说明功能和参数
- 变量和函数名使用小写字母和下划线组合
- 类名使用驼峰命名法
- 代码注释清晰明了，解释复杂逻辑和关键步骤
- 避免使用魔法数字，使用常量代替
- 函数长度不超过50行，类不超过300行

### 提交代码

1. 创建特性分支：`git checkout -b feature/your-feature`
2. 编写代码并提交：`git add . && git commit -m "Add your feature"`
3. 推送到远程分支：`git push origin feature/your-feature`
4. 创建Pull Request，描述功能和修改内容

### 代码审查

- 确保代码符合项目规范和架构设计
- 检查代码逻辑和性能问题
- 提供建设性的反馈和改进建议
- 确保测试用例覆盖新功能

## 📄 许可证

本项目采用MIT许可证 - 查看[LICENSE](LICENSE)文件了解详情

## 鸣谢

- [art-design-pro](https://github.com/Daymychen/art-design-pro) - 提供管理后台模板
- [Flask](https://flask.palletsprojects.com/) - Python Web框架
- [MySQL](https://www.mysql.com/) - 关系型数据库管理系统
- [Vue.js](https://vuejs.org/) - 前端渐进式框架
- [Element UI](https://element.eleme.cn/) - 前端UI组件库

## 📞 联系方式

如有问题或建议，欢迎通过以下方式联系：

- GitHub Issues: https://github.com/itrfcn/Pymusic/issues


## 📚 附录

### 故障排除

#### 数据库连接错误

**问题**：无法连接到数据库，提示"Access denied for user 'root'@'localhost'"

**解决方案**：
1. 检查MySQL是否已启动
   - Windows: `net start mysql`
   - Linux: `sudo systemctl start mysql`
   - macOS: `brew services start mysql`
2. 检查.env文件中的数据库配置是否正确
3. 确保MySQL用户有足够的权限访问指定数据库
   ```sql
   GRANT ALL PRIVILEGES ON music.* TO 'root'@'localhost' IDENTIFIED BY 'your-password';
   FLUSH PRIVILEGES;
   ```
4. 尝试重置MySQL用户密码
   ```sql
   ALTER USER 'root'@'localhost' IDENTIFIED BY 'new-password';
   FLUSH PRIVILEGES;
   ```

#### 依赖安装失败

**问题**：安装依赖时出现"Could not find a version that satisfies the requirement"

**解决方案**：
1. 更新pip：`pip install --upgrade pip`
2. 检查Python版本是否符合要求（>=3.8）
3. 尝试使用虚拟环境重新安装
4. 手动安装特定版本的依赖包：`pip install flask==3.0.3`

#### 音乐播放失败

**问题**：无法播放音乐，提示"无法加载音频文件"

**解决方案**：
1. 检查网络连接是否正常
2. 确保网易云音乐API可用
3. 检查浏览器控制台是否有错误信息
4. 尝试刷新页面或重新登录
5. 检查.env文件中的网易云音乐Cookie是否配置正确

#### 管理后台无法访问

**问题**：访问/admin/时出现404错误

**解决方案**：
1. 确保Vue打包资源已正确放置在static/assets目录
2. 检查templates/admin/index.html文件中的资源引用路径
3. 确保admin蓝图已正确注册
4. 检查管理员账号是否有访问权限
5. 查看浏览器控制台是否有资源加载错误

#### Vue管理页面资源404错误

**问题**：访问/admin/时出现"GET http://127.0.0.1:5000/static/admin/assets/index-Pun-ULnE.js net::ERR_ABORTED 404 (NOT FOUND)"

**解决方案**：
1. 检查static/assets目录下是否存在该文件
2. 确保Vue打包后的资源文件已正确复制到static/assets目录
3. 检查templates/admin/index.html文件中的资源引用路径是否正确
4. 重新打包Vue项目并复制资源文件


### 管理员账号安全建议

1. **使用强密码**：管理员密码应包含大小写字母、数字和特殊字符，长度至少8位
2. **定期更换密码**：建议每3个月更换一次管理员密码
3. **限制登录IP**：在生产环境中，建议限制管理员账号只能从特定IP登录
4. **启用双因素认证**：条件允许时，启用双因素认证增加账号安全性
5. **定期审计日志**：定期查看系统日志，检查是否有异常登录和操作记录
6. **最小权限原则**：管理员账号只用于管理操作，不用于日常使用

---

**Py Music** - 让音乐触手可及 🎵