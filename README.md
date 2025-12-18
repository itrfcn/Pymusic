# Pymusic - 在线音乐播放平台

## 📖 项目概述

Pymusic是一个基于Flask框架和Vue.js开发的现代化在线音乐播放平台，集成了网易云音乐API，提供完整的音乐播放、用户管理和数据分析功能。该平台采用前后端分离架构，后端使用Flask提供RESTful API，前端使用原生HTML/CSS/JavaScript和Vue.js（管理后台）构建用户界面。

## 🎨 设计理念

- **用户体验优先**：简洁直观的界面设计，流畅的音乐播放体验
- **模块化架构**：采用Flask蓝图实现功能模块分离，便于维护和扩展
- **安全性第一**：全面的安全防护措施，包括IP访问限制、SQL注入检测和XSS防护
- **数据驱动决策**：丰富的数据分析功能，帮助管理员了解用户行为和系统性能

## 🎯 项目目标

- **完整音乐解决方案**：提供全方位的在线音乐播放服务
- **个性化体验**：打造专属的用户音乐推荐和播放体验
- **可扩展架构**：构建灵活的前后端分离系统，支持功能扩展
- **管理数据分析**：提供全面的管理工具和数据分析功能
- **稳定安全保障**：确保系统的高可用性、安全性和稳定性


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
| ArtDesignPro | 3.0.0 | 管理后台模板 | 提供响应式布局、组件库、示例代码 |
| Element UI | 3.x | UI组件库 | 美观的组件、完善的文档、易于使用 |

### 数据库
| 数据库 | 版本 | 用途 | 选型理由 |
|-------|------|------|---------|
| MySQL | 5.7+ | 数据存储 | 成熟稳定、高性能、广泛使用 |



## 📁 项目结构

```
wangyi/
├── apps/                    # 应用模块
│   ├── tool/               # 工具类
│   │   ├── File.py         # 文件操作工具
│   │   ├── JS.py           # JavaScript处理工具
│   │   └── Mysql.py        # MySQL数据库工具
│   ├── admin.py            # 管理后台模块
│   ├── analytics.py        # 数据分析模块
│   ├── clean_history_data.py # 历史数据清理
│   ├── music.py            # 音乐核心功能模块
│   └── user.py             # 用户模块
├── static/                 # 静态资源
│   ├── assets/            # 编译后的前端资源
│   ├── css/               # CSS文件
│   ├── img/               # 图片资源
│   └── js/                # JavaScript文件
├── templates/              # 模板文件
│   ├── admin/             # 管理后台模板
│   ├── partials/          # 页面片段
│   ├── user/              # 用户相关模板
│   ├── 404.html           # 404页面
│   ├── 500.html           # 500页面
│   └── index.html         # 主页
├── app.py                 # 应用入口
├── config.py              # 配置文件
├── database_schema.sql    # 数据库结构
├── requirements.txt       # 依赖列表
├── .env.example           # 环境变量示例
├── .gitignore             # Git忽略文件
└── LICENSE                # 许可证
```

## 🚀 安装部署

### 环境要求
- Python 3.8+
- MySQL 5.7+
- Node.js 14+ (可选，用于Vue.js前端开发)

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/itrfcn/Pymusic.git
   cd Pymusic-main
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```
**注意事项**：
- 建议使用虚拟环境（virtualenv或conda）安装依赖，避免与系统Python环境冲突
- 如果安装过程中遇到依赖冲突或其他问题，请参考附录中的"故障排除"部分

4. **配置环境变量**
   ```bash
   cp .env.example .env
   # 根据注释修改.env文件中的参数
   ```

5. **初始化数据库**
   ```bash
   # 创建数据库
   mysql -u root -p -e "CREATE DATABASE music;
   # 导入数据库结构
   mysql -u root -p music < database_schema.sql
   ```

6. **启动应用**
   ```bash
   # 开发模式
   flask run
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

## 📝 API文档

### 音乐相关API

#### 搜索音乐
```
GET /music/search?name={关键词}&page={页码}
```

#### 解析音乐
```
GET /music/jx?ids={song_id}&level={音质}&type={返回类型}
```
参数说明：
- `song_id`：音乐ID
- `音质`：可选值为`standard`（标准音质）、`high`（高音质）、`lossless`（无损音质）
- `返回类型`：可选值为`json`（返回JSON格式）、`html`（返回HTML格式）

#### 获取歌单详情
```
GET /music/playlist/{playlist_id}
```

### 用户相关API

#### 用户登录
```
POST /user/login
```

#### 用户注册
```
POST /user/register
```

#### 获取个人信息
```
GET /user/profile
```

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

## 🔒 安全特性

### 防护措施
- **IP访问限制**：限制每个IP的请求频率
- **SQL注入防护**：使用参数化查询和正则检测
- **XSS防护**：输入过滤和输出编码
- **异常User-Agent检测**：拦截异常访问
- **请求内容检查**：检测恶意请求内容

### 安全配置

在`.env`文件中可以配置以下安全参数：

```bash
# IP访问限制
IP_RATE_LIMIT_ENABLED=True
IP_RATE_LIMIT=100
IP_RATE_LIMIT_WINDOW=60

# 恶意请求检测
MALICIOUS_REQUEST_DETECTION=True

# IP黑白名单
IP_WHITELIST=127.0.0.1
IP_BLACKLIST=192.168.1.100
```

## 🚀 部署建议

### 生产环境

1. **使用Gunicorn**：代替Flask内置服务器
2. **配置Nginx**：作为反向代理
3. **启用HTTPS**：使用SSL证书
4. **设置防火墙**：限制访问端口
5. **定期备份**：数据库和日志定期备份

### 性能优化

1. **数据库索引**：合理设置数据库索引
2. **缓存机制**：使用Redis缓存热点数据
3. **异步任务**：使用Celery处理异步任务
4. **静态资源CDN**：使用CDN加速静态资源

## 📚 常见问题

### Q: 无法播放音乐怎么办？
A: 请检查网易云音乐Cookie是否配置正确，或者网络连接是否正常。

### Q: 搜索结果不准确？
A: 请尝试调整搜索关键词，或者检查网易云音乐API是否有更新。

### Q: 系统运行缓慢？
A: 请检查服务器资源使用情况，或者优化数据库查询。


## 📄 许可证

本项目采用MIT许可证 - 查看[LICENSE](LICENSE)文件了解详情

## 🙏 鸣谢

- [ArtDesignPro](https://github.com/Daymychen/art-design-pro) - 提供管理后台模板
- [Flask](https://flask.palletsprojects.com/) - Python Web框架
- [MySQL](https://www.mysql.com/) - 关系型数据库管理系统
- [Vue.js](https://vuejs.org/) - 前端渐进式框架
- [Element UI](https://element.eleme.cn/) - 前端UI组件库

## 🌟 优秀项目推荐

以下是一些与本项目相关的优秀开源项目，供您参考学习：

- 🎵 **[UniMusic](https://github.com/FOxfys/uniapp-music)** - 基于本项目开发的uni-app多平台音乐应用

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 贡献步骤

1. **Fork项目**：点击项目页面右上角的Fork按钮
2. **克隆项目**：`git clone https://github.com/itrfcn/Pymusic.git`
3. **创建分支**：`git checkout -b feature/your-feature`
4. **提交更改**：`git commit -am 'Add some feature'`
5. **推送到分支**：`git push origin feature/your-feature`

### 提交Issue

- 描述问题或建议
- 提供复现步骤（如果有）
- 附上相关日志或截图

### 提交Pull Request

- 基于最新的`dev`分支
- 描述变更内容
- 确保代码符合项目规范
- 提交PR后，会进行审核和合并

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- GitHub: [https://github.com/itrfcn/Pymusic/issues](https://github.com/itrfcn/Pymusic/issues)

---

**注意**：本项目仅供学习和研究使用，请勿用于商业用途。请遵守网易云音乐的相关服务条款。