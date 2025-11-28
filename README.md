# Pymusic-在线音乐播放平台

## 项目简介

这是一个基于Flask框架开发的个人音乐播放器项目，旨在模拟网易云音乐的核心功能并提供简洁的用户体验。该项目集成了网易云音乐API，支持音乐搜索、歌单管理、用户认证等功能，为音乐爱好者提供一个轻量级的音乐播放和管理平台。

### 项目特色

- 简洁美观的用户界面，支持响应式设计
- 完整的音乐播放功能，包括播放控制、歌词显示
- 个人歌单管理系统，支持创建和编辑
- 用户认证系统，保护个人数据
- 详细的播放历史记录
- 热门歌单推荐功能

## 技术栈

### 后端

- **框架**: Flask
- **数据库**: MySQL (使用pymysql驱动)
- **认证**: Flask-Session
- **日志**: Python logging模块

### 前端

- **HTML5/CSS3/JavaScript**
- **UI组件**: Font Awesome图标库
- **响应式设计**: 支持移动端和桌面端

## 功能特性

### 音乐播放与发现

- 热门歌单推荐
- 音乐搜索功能
- 歌曲详情查看
- 歌词获取与显示
- 音乐解析功能

### 用户系统

- 用户注册与登录
- 个人播放历史记录
- 播放历史分页查询
- 会话管理与身份验证

### 歌单管理

- 个人歌单创建
- 添加/删除歌单歌曲
- 歌单信息编辑与删除
- 歌单详情查看

### 其他功能

- 完整的错误处理机制
- 详细的日志记录
- 开发/生产环境配置分离
- 数据库连接池管理

## 项目结构

```
Pymusic/
├── app.py                  # 应用入口文件，配置路由和中间件
├── config.py               # 应用配置文件，加载环境变量
├── .env.example            # 环境变量示例文件
├── .gitignore              # Git忽略文件配置
├── database_schema.sql     # 数据库表结构定义文件
├── LICENSE                 # 项目许可证文件
├── README.md               # 项目说明文档
├── requirements.txt        # 项目依赖列表
├── apps/
│   ├── clean_history_data.py  # 数据清理模块，定期清理播放历史
│   ├── music.py            # 音乐相关功能模块，处理音乐搜索和播放
│   ├── user.py             # 用户相关功能模块，处理用户认证和歌单管理
│   └── tool/
│       ├── File.py         # 文件操作工具，处理文件读写
│       ├── JS.py           # JS相关工具，处理API调用和数据转换
│       └── Mysql.py        # 数据库操作工具，封装MySQL连接和查询
├── static/                 # 静态资源文件
│   ├── css/                # CSS样式文件
│   │   └── main.css        # 主样式表
│   ├── favicon.ico         # 网站图标
│   ├── img/                # 图片资源
│   │   └── logo.png        # 项目logo
│   └── js/                 # JavaScript文件
│       └── main.js         # 主脚本文件
└── templates/              # HTML模板文件
    ├── 404.html            # 404错误页面
    ├── 500.html            # 500错误页面
    ├── index.html          # 首页模板
    ├── partials/           # 部分页面模板
    │   ├── about.html      # 关于页面
    │   ├── discover.html   # 发现页面
    │   ├── doc-163.html    # 解析页面
    │   ├── history.html    # 历史页面
    │   ├── playlist_detail.html # 歌单详情页面
    │   └── rank.html       # 排行榜页面
    └── user/               # 用户相关页面模板
        ├── login.html      # 登录页面
        └── register.html   # 注册页面
```

## 数据库结构

### 用户表 (user)
| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| `id` | INT | PRIMARY KEY AUTO_INCREMENT | 用户ID |
| `username` | VARCHAR(50) | NOT NULL UNIQUE | 用户名 |
| `password` | VARCHAR(100) | NOT NULL | 加密后的密码 |
| `create_time` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP NULL | 创建时间 |
| `update_time` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

### 播放历史表 (play_history)
| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| `id` | INT | PRIMARY KEY AUTO_INCREMENT | 记录ID |
| `user_id` | INT | NOT NULL | 用户ID |
| `song_id` | BIGINT | NOT NULL | 网易云音乐歌曲ID |
| `play_time` | DATETIME | DEFAULT CURRENT_TIMESTAMP NULL | 播放时间 |

**表约束和索引：**
- 唯一约束: `idx_user_song` - `user_id`和`song_id`组合，避免重复记录
- 索引: `idx_user_id` - 基于`user_id`的单列索引
- 索引: `idx_song_id` - 基于`song_id`的单列索引
- 索引: `idx_user_time` - `user_id`和`play_time`(降序)组合索引，优化按时间查询

### 播放列表表 (playlist)
| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| `id` | INT | PRIMARY KEY AUTO_INCREMENT | 歌单ID |
| `user_id` | INT | NOT NULL | 创建者用户ID |
| `name` | VARCHAR(100) | NOT NULL | 歌单名称 |
| `cover_url` | LONGTEXT | NULL | 歌单封面图片URL |
| `description` | TEXT | NULL | 歌单描述 |
| `create_time` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP NULL | 创建时间 |
| `update_time` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

**表约束和索引：**
- 唯一约束: `unique_user_playlist` - `user_id`和`name`组合，确保用户歌单名称唯一
- 外键约束: `playlist_ibfk_1` - `user_id`引用`tabl_user`表的`id`(注意：表名可能有误，应为`user`)
- 索引: `idx_playlist_user_id` - 基于`user_id`的单列索引

### 播放列表歌曲表 (playlist_song)
| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| `id` | INT | PRIMARY KEY AUTO_INCREMENT | 记录ID |
| `playlist_id` | INT | NOT NULL | 歌单ID |
| `song_id` | BIGINT | NOT NULL | 网易云音乐歌曲ID |
| `add_time` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP NULL | 添加时间 |

**表约束和索引：**
- 唯一约束: `unique_playlist_song` - `playlist_id`和`song_id`组合，避免重复添加歌曲
- 外键约束: `playlist_song_ibfk_1` - `playlist_id`引用`playlist`表的`id`，级联删除
- 索引: `idx_playlist_song_playlist_id` - 基于`playlist_id`的单列索引
- 索引: `idx_playlist_song_song_id` - 基于`song_id`的单列索引

**表关系说明：**
- 用户可以创建多个歌单 (`user` 1:N `playlist`)
- 一个歌单可以包含多首歌曲 (`playlist` 1:N `playlist_song`)
- 一个用户可以有多条播放历史 (`user` 1:N `play_history`)

**查询性能优化建议：**
- 对于播放历史查询，可以使用`play_time`字段进行分页
- 对于歌单歌曲查询，使用`playlist_id`字段进行索引查询
- 建议定期清理过期的播放历史数据以保持性能

## 快速开始

### 环境要求
- Python 3.6+
- MySQL 5.7+

### 安装步骤

#### 方法一：本地开发环境部署

1. **克隆项目**
   ```bash
   git clone https://github.com/itrfcn/Pymusic.git
   # 进入项目目录
   cd Pymusic
   ```

2. **安装依赖**
   ```bash
   # 推荐在虚拟环境中安装依赖
   # 创建虚拟环境 (可选但推荐)
   python -m venv venv
   # 激活虚拟环境
   # Windows: 
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   
   # 安装项目依赖
   pip install -r requirements.txt
   ```

3. **配置环境变量**
   创建`.env`文件复制`.env.example`内容并填写相应值：
   ```
   # Flask配置
   SECRET_KEY=your-secret-key-here  # 应用密钥，生产环境必须设置安全的随机值
   FLASK_DEBUG=True  # 是否开启调试模式，生产环境设为False
   FLASK_ENV=development  # 环境设置：development, production, testing
   FLASK_APP=app.py

   # 服务器配置
   HOST=0.0.0.0  # 服务器监听地址
   PORT=5000  # 服务器监听端口

   # 数据库配置
   DB_HOST=localhost  # 数据库主机地址
   DB_USER=root  # 数据库用户名
   DB_PASSWORD=your-database-password  # 数据库密码
   DB_NAME=music  # 数据库名称
   DB_PORT=3306  # 数据库端口
   TEST_DB_NAME=analysis_test  # 测试环境数据库名称

   # 网易云音乐API配置
   NETEASE_MUSIC_AES_KEY=e82ckenh8dichen8 # 网易云音乐API加密密钥，使用默认的即可
   NETEASE_MUSIC_COOKIE=your-netease-music-cookie-here # 网易云音乐Cookie，登录网页版后获取

   # 日志配置
   LOG_LEVEL=INFO  # 日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL
   LOG_FILE=logs/app.log  # 日志文件路径
   LOG_MAX_BYTES=5242880  # 单个日志文件最大字节数（默认5MB）
   LOG_BACKUP_COUNT=30  # 保留的日志文件备份数量
   ```
   
   **注意事项：**
   - 生产环境中必须设置强安全的`SECRET_KEY`
   - `DB_PASSWORD`请根据实际数据库密码修改
   - `NETEASE_MUSIC_COOKIE`需要从网易云音乐网页版登录后获取，某些功能（如私人歌单）需要有效Cookie才能使用

4. **初始化数据库**
   执行`database_schema.sql`中的SQL语句创建数据库表结构：
   ```bash
   # 确保MySQL服务已启动
   # 输入MySQL密码时会有提示
   mysql -u root -p < database_schema.sql
   ```

5. **启动应用**
   ```bash
   # 开发模式启动
   flask run
   ```

#### 方法二：Docker部署

1. **创建Dockerfile**
   在项目根目录创建`Dockerfile`文件：
   ```dockerfile
   # 使用官方Python镜像作为基础镜像
   FROM python:3.8-slim

   # 设置工作目录
   WORKDIR /app

   # 复制依赖文件
   COPY requirements.txt .

   # 安装依赖
   RUN pip install --no-cache-dir -r requirements.txt

   # 复制项目文件
   COPY . .

   # 设置环境变量
   ENV FLASK_ENV=production
   ENV FLASK_APP=app.py

   # 暴露端口
   EXPOSE 5000

   # 启动应用
   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
   ```

2. **创建docker-compose.yml**
   ```yaml
   version: '3'
   services:
     web:
       build: .
       ports:
         - "5000:5000"
       environment:
         - DB_HOST=db
         - DB_USER=root
         - DB_PASSWORD=your_secure_password
         - DB_NAME=music
         - NETEASE_API_KEY=
         - NETEASE_COOKIE=
       depends_on:
         - db
     db:
       image: mysql:5.7
       environment:
         - MYSQL_ROOT_PASSWORD=your_secure_password
         - MYSQL_DATABASE=music
       volumes:
         - mysql_data:/var/lib/mysql
         - ./database_schema.sql:/docker-entrypoint-initdb.d/init.sql

   volumes:
     mysql_data:
   ```

3. **构建并启动容器**
   ```bash
   docker-compose up -d
   ```

### 生产环境配置建议

1. **使用Gunicorn作为WSGI服务器**
   ```bash
   # 安装Gunicorn
   pip install gunicorn
   
   # 启动应用，4个工作进程，监听所有接口的5000端口
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   
   # 使用超时设置和日志输出
   # gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 --log-level info app:app
   ```

2. **配置Nginx作为反向代理**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
   }
   ```

3. **使用Supervisor管理进程**
   ```ini
   [program:wangyi]
   command=/path/to/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
   directory=/path/to/wangyi
   user=www-data
   autostart=true
   autorestart=true
   redirect_stderr=true
   stdout_logfile=/path/to/logs/wangyi.log
   ```

4. **定期备份数据库**
   ```bash
   # 导出完整数据库
   mysqldump -u root -p music > music_backup_$(date +%Y%m%d).sql
   
   # 可以添加到crontab中实现自动备份
   # 例如每天凌晨2点备份
   # 0 2 * * * mysqldump -u root -p'yourpassword' music > /path/to/backups/music_backup_$(date +\%Y\%m\%d).sql
   ```

5. **配置HTTPS**
   - 使用Let's Encrypt获取免费SSL证书
   - 配置Nginx支持HTTPS连接

## 注意事项

1. **网易云音乐API访问限制**
   - 本项目依赖网易云音乐API，请注意API的使用频率限制
   - 建议在生产环境中配置有效的API密钥和Cookie
   - 定期更新Cookie以保证API正常访问

2. **安全配置**
   - 在生产环境中，请修改默认数据库密码
   - 确保关闭调试模式（DEBUG=False）
   - 配置适当的日志级别和存储位置
   - 考虑使用HTTPS保护数据传输

3. **性能优化**
   - 对于大量数据查询，建议增加缓存机制
   - 考虑使用异步处理长时间运行的操作
   - 对于频繁访问的歌单和歌曲信息，可以实现本地缓存

4. **数据清理**
   - 定期运行`clean_history_data.py`清理过期的播放历史记录
   - 考虑实现自动化的数据备份策略

## 许可证

本项目采用MIT许可证 - 详情请查看LICENSE文件

## 贡献指南


欢迎提交Issue和Pull Request！如果您想为项目做出贡献，请遵循以下步骤：

1. Fork本仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个Pull Request

## 开发日志

- 初始版本：实现了基本的音乐播放和搜索功能
- 版本1.1：添加了用户系统和歌单管理功能
- 版本1.2：优化了前端界面，增加了响应式设计
- 版本1.3：完善了错误处理和日志系统

## 免责声明


本项目仅作为学习和个人使用目的，与网易云音乐官方无任何关系。使用本项目时，请遵守相关法律法规和网易云音乐的服务条款。开发者不对使用本项目可能引起的任何后果负责。

## 常见问题 (FAQ)

### 网易云音乐API相关问题

#### 1. 为什么API调用失败或返回空数据？

**A:** 可能的原因：
- 网易云音乐API有访问频率限制，超过限制会被临时封禁
- Cookie过期，需要更新`NETEASE_COOKIE`环境变量
- 网络环境问题，检查是否能正常访问网易云音乐官网

#### 2. 如何获取有效的网易云音乐Cookie？
**A:** 可以通过以下步骤获取：
1. 登录网易云音乐官网(https://music.163.com)
2. 使用浏览器开发者工具(F12)，查看网络请求中的Cookie
3. 复制完整的Cookie字符串到环境变量中

### 数据库相关问题


#### 3. 数据库连接失败怎么办？
**A:** 检查以下几点：
- MySQL服务是否已启动
- 环境变量中的数据库配置是否正确
- 数据库用户是否有足够的权限
- 防火墙是否阻止了MySQL连接

#### 4. 如何解决数据库表结构不匹配的问题？
**A:** 建议重新初始化数据库：
```bash
# 先删除现有数据库(注意备份)
mysql -u root -p -e "DROP DATABASE IF EXISTS music; CREATE DATABASE music;"
# 重新导入数据库结构
mysql -u root -p < database_schema.sql
```

### 部署与运行问题


#### 5. 生产环境中如何优化性能？
**A:** 推荐以下优化措施：
- 使用Gunicorn或uWSGI替代Flask开发服务器
- 配置Nginx作为反向代理，启用静态文件缓存
- 实现API结果缓存，减少重复查询
- 优化数据库索引，定期清理无效数据

#### 6. Docker部署时数据库连接失败如何解决？
**A:** 检查：
- 确保docker-compose.yml中的数据库配置正确
- 检查容器网络是否正常连通
- 查看日志确定具体错误原因：`docker-compose logs -f`

### 用户认证问题


#### 7. 用户登录失败如何排查？
**A:** 排查步骤：
- 检查用户名和密码是否正确
- 查看应用日志，检查是否有异常信息
- 验证数据库中用户表的数据是否正常

#### 8. 如何实现密码重置功能？
**A:** 目前项目未实现密码重置功能，您可以通过以下方式手动重置：
```sql
UPDATE user SET password = SHA2('新密码', 256) WHERE username = '用户名';
```

### 其他问题


#### 9. 如何添加新的API接口？
**A:** 在相应的功能模块文件中添加路由和处理函数，例如：
```python
# 在apps/music.py中
@app.route('/new_api', methods=['GET'])
def new_api_handler():
    # 实现API逻辑
    return jsonify({'status': 'success', 'data': '...'})
```

#### 10. 如何修改前端界面？
**A:** 前端代码位于`templates/`和`static/`目录，您可以：
- 修改`templates/`中的HTML模板
- 编辑`static/css/`中的样式文件
- 更新`static/js/`中的JavaScript代码

## 联系我们

如有任何问题或建议，请通过以下方式联系我们：

- [Issues](https://github.com/yourusername/wangyi/issues)
