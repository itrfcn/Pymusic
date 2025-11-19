# 网易云音乐播放器 - 个人项目版

![项目logo](static/img/logo.png)

## 🌟 项目简介

这是一个基于Flask框架开发的个人音乐播放器项目，旨在模拟网易云音乐的核心功能并提供简洁的用户体验。该项目集成了网易云音乐API，支持音乐搜索、歌单管理、用户认证等功能，为音乐爱好者提供一个轻量级的音乐播放和管理平台。

## 🚀 功能特性

- **音乐搜索**：支持按歌曲名称、歌手搜索网易云音乐资源，提供分页结果显示
- **歌单管理**：创建、编辑、删除个人歌单，添加/删除歌单歌曲，支持歌单封面设置
- **用户系统**：完整的用户注册、登录、身份验证机制，保护用户数据安全
- **播放历史**：自动记录和管理用户的播放历史，支持查看最近播放记录
- **热门推荐**：获取网易云音乐热门歌单推荐，发现更多好音乐
- **音乐播放**：支持歌曲播放、暂停、歌词显示、封面查看等基本功能
- **数据管理**：内置播放历史数据清理工具，保持数据库高效运行

## 🛠 技术栈

- **后端框架**：Flask 2.x (Python)
- **数据库**：MySQL 5.7+ (使用自定义工具类操作)
- **前端技术**：HTML5, CSS3, JavaScript
- **API集成**：网易云音乐API (非官方,爬虫获取)
- **认证机制**：Session-based认证
- **配置管理**：环境变量 + 配置文件
- **工具库**：自定义数据库、文件和JS操作工具类

## 📦 安装指南

### 前提条件

- Python 3.7 或更高版本
- MySQL 5.7 或更高版本
- Git (用于克隆仓库)

### 安装步骤

1. **克隆项目**

   ```bash
   git clone https://github.com/itrfcn/Pymusic.git
   cd Pymusic
   ```

2. **创建虚拟环境**

   ```bash
   python -m venv venv
   ```

3. **激活虚拟环境**

   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **安装项目依赖**

   ```bash
   pip install -r requirements.txt
   ```

5. **配置环境变量**

   复制 `.env.example` 文件并重命名为 `.env`，然后根据您的环境修改相应配置：

   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填写数据库信息和其他配置
   ```

   **重要配置说明：**
   - `SECRET_KEY`：用于Flask会话加密，请设置一个复杂的随机字符串
   - 数据库配置：根据您的MySQL安装情况填写主机、用户名、密码等
   - 日志配置：可根据需要调整日志级别和文件路径

6. **配置网易云音乐Cookie**

   创建 `cookie.txt` 文件，登录网易云音乐网页版后获取Cookie，将其粘贴到文件中：

   ```bash
   MUSIC_U=xxxxx;
   ```

7. **初始化数据库**

   - 创建MySQL数据库：
     ```sql
     CREATE DATABASE music DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
     ```

   - 导入数据库表结构：
     ```bash
     mysql -u your_username -p music < database_schema.sql
     ```

8. **启动应用**

   ```bash
   python app.py
   ```

9. **访问应用**

   打开浏览器，访问：http://localhost:5000

## 🔧 环境配置说明

应用通过 `.env` 文件进行配置，主要配置项包括：

| 配置项 | 描述 | 默认值 | 示例 |
|-------|------|-------|------|
| SECRET_KEY | Flask应用密钥 | 无（必须设置） | `a_random_secret_key_here` |
| FLASK_DEBUG | 是否开启调试模式 | False | `True`或`False` |
| FLASK_ENV | 运行环境 | production | `development`或`production` |
| DB_HOST | 数据库主机地址 | localhost | `localhost`或IP地址 |
| DB_USER | 数据库用户名 | root | `your_username` |
| DB_PASSWORD | 数据库密码 | 无 | `your_password` |
| DB_NAME | 数据库名称 | music | `your_database` |
| DB_PORT | 数据库端口 | 3306 | `3306`或自定义端口 |
| NETEASE_MUSIC_AES_KEY | 网易云音乐API密钥 | 无 | 从API文档获取 |
| LOG_LEVEL | 日志级别 | INFO | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| LOG_FILE | 日志文件路径 | app.log | `logs/app.log` |

## 🎯 使用说明

### 1. 用户注册与登录
- 首次访问时自动跳转到登录页面
- 点击"注册"链接进行新用户注册
- 注册成功后自动登录系统

### 2. 音乐搜索
- 在首页搜索框中输入歌曲名称或歌手名称
- 点击搜索按钮或按回车查看搜索结果
- 支持分页浏览搜索结果

### 3. 歌单管理
- 登录后，点击侧边栏的"创建歌单"按钮
- 在歌单页面输入歌单名称和描述
- 通过搜索功能找到歌曲，点击"添加到歌单"按钮
- 在歌单详情页面可以删除歌曲或编辑歌单信息

### 4. 播放历史
- 播放歌曲时系统会自动记录播放历史
- 可以在个人中心或专门的历史页面查看播放记录
- 定期自动清理过期的播放历史数据

### 5. 热门推荐
- 在发现页面可以查看网易云音乐热门歌单
- 点击感兴趣的歌单可以查看详情并播放其中的歌曲

## 📡 API接口文档

### 音乐相关接口

| 接口路径 | 方法 | 功能描述 | 参数说明 |
|---------|------|---------|--------|
| `/jx` | GET | 歌曲解析 | 无 |
| `/search/<name>/<page>` | GET | 搜索歌曲 | name: 搜索关键词<br>page: 页码 |
| `/playlist/<sid>` | GET | 获取歌单详情 | sid: 歌单ID |
| `/song/url/<song_id>` | GET | 获取歌曲URL | song_id: 歌曲ID |
| `/song/lyric/<song_id>` | GET | 获取歌词 | song_id: 歌曲ID |
| `/song/cover/<song_id>` | GET | 获取歌曲封面 | song_id: 歌曲ID |

### 用户相关接口

| 接口路径 | 方法 | 功能描述 | 参数说明 |
|---------|------|---------|--------|
| `/user/login` | POST | 用户登录 | username: 用户名<br>password: 密码 |
| `/user/register` | POST | 用户注册 | username: 用户名<br>password: 密码 |
| `/user/playlists` | GET | 获取用户歌单 | 无（需要登录） |
| `/user/create_playlist` | POST | 创建歌单 | name: 歌单名称<br>description: 歌单描述 |
| `/user/playlist/<playlist_id>` | GET/POST/DELETE | 获取/更新/删除歌单 | playlist_id: 歌单ID |

## 📁 项目结构

```
wangyi/
├── app.py                  # 应用入口文件，配置路由和中间件
├── config.py               # 应用配置文件，加载环境变量
├── .env.example            # 环境变量示例文件
├── database_schema.sql     # 数据库表结构定义文件
├── apps/
│   ├── music.py            # 音乐相关功能模块，处理音乐搜索和播放
│   ├── user.py             # 用户相关功能模块，处理用户认证和歌单管理
│   ├── clean_history_data.py  # 数据清理模块，定期清理播放历史
│   └── tool/               # 工具类目录
│       ├── Mysql.py        # 数据库操作工具，封装MySQL连接和查询
│       ├── JS.py           # JS相关工具，处理API调用和数据转换
│       └── File.py         # 文件操作工具，处理文件读写
├── static/                 # 静态资源文件
│   ├── css/                # CSS样式文件
│   │   └── main.css        # 主样式表
│   ├── js/                 # JavaScript文件
│   │   └── main.js         # 主脚本文件
│   └── img/                # 图片资源
│       └── logo.png        # 项目logo
├── templates/              # HTML模板文件
│   ├── index.html          # 首页模板
│   ├── 404.html            # 404错误页面
│   ├── partials/           # 部分页面模板
│   │   ├── about.html      # 关于页面
│   │   ├── discover.html   # 发现页面
│   │   ├── doc-163.html    # 文档页面
│   │   ├── history.html    # 历史页面
│   │   ├── playlist_detail.html # 歌单详情页面
│   │   └── rank.html       # 排行榜页面
│   └── user/               # 用户相关页面模板
│       ├── login.html      # 登录页面
│       └── register.html   # 注册页面
├── requirements.txt        # 项目依赖列表
├── LICENSE                 # 许可证文件
└── README.md               # 项目说明文档
```

## ⚠️ 注意事项

1. **仅供学习使用**：本项目仅供个人学习和研究使用，请勿用于商业目的
2. **版权尊重**：项目中使用的音乐资源均来自网易云音乐API，请尊重音乐版权
3. **法律合规**：使用本项目时，请遵守相关法律法规和网易云音乐的服务条款
4. **安全设置**：生产环境中，请确保设置安全的`SECRET_KEY`和数据库密码
5. **数据备份**：定期备份数据库数据，以防数据丢失
6. **Cookie更新**：如果发现无法获取音乐资源，请检查并更新网易云音乐Cookie
7. **API限制**：非官方API可能随时变更，导致部分功能不可用

## 🔒 安全建议

1. **密码管理**：确保用户密码在数据库中加密存储
2. **SQL注入防护**：使用参数化查询，避免SQL注入攻击
3. **XSS防护**：对用户输入进行过滤和转义，防止跨站脚本攻击
4. **CSRF防护**：实现CSRF令牌验证，防止跨站请求伪造
5. **访问控制**：确保敏感功能只对已登录用户开放
6. **错误处理**：生产环境中不要向用户暴露详细的错误信息

## 📜 许可证

本项目采用MIT许可证 - 详情请查看 [LICENSE](LICENSE) 文件

## 📝 免责声明

本项目仅作为学习和个人使用目的，与网易云音乐官方无任何关系。使用本项目时，请遵守相关法律法规和网易云音乐的服务条款。开发者不对使用本项目可能引起的任何后果负责。