import pymysql
from dbutils.pooled_db import PooledDB
from config import current_config


# 创建全局连接池实例
pool = None


class Mysql:
    def __init__(self):
        global pool
        if not pool:
            # 初始化连接池
            pool = PooledDB(
                creator=pymysql,  # 使用pymysql作为数据库连接模块
                maxconnections=50,  # 连接池允许的最大连接数
                mincached=5,  # 初始化时连接池的空闲连接数量
                maxcached=20,  # 连接池中空闲连接的最大数量
                maxshared=0,  # 连接池允许的最大共享连接数（0表示所有连接都是专用的）
                blocking=True,  # 当没有可用连接时是否阻塞等待
                maxusage=None,  # 单个连接的最大使用次数（None表示无限制）
                setsession=[],  # 开始会话前执行的命令列表
                ping=4,  # 检查连接是否有效的方式
                host=getattr(current_config, 'DB_HOST', 'localhost'),
                user=getattr(current_config, 'DB_USER', 'root'),
                password=getattr(current_config, 'DB_PASSWORD', '123456'),
                database=getattr(current_config, 'DB_NAME', 'music'),
                port=getattr(current_config, 'DB_PORT', 3306),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
        
        # 从连接池中获取一个连接
        self.db = pool.connection()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def update(self, sql, param=()):
        sql = sql.strip()
        count = rowid = None
        cursor = self.db.cursor()
        try:
            # 统一使用execute执行单条SQL语句
            count = cursor.execute(sql, param)
            self.db.commit()
            rowid = cursor.lastrowid
        except Exception as e:
            print(e)
            self.db.rollback()
        finally:
            cursor.close()
        return count, rowid

    def select(self, sql, param=(), limit=0):
        sql = sql.strip()
        result = None
        cursor = self.db.cursor()
        try:
            cursor.execute(sql, param)
            result = cursor.fetchall() if limit == 0 else cursor.fetchmany(limit)
        except Exception as e:
            print(e)
        finally:
            cursor.close()
        return result

    def sql(self, sql, param=(), limit=0):
        sql = sql.strip().lower()  # 转换为小写
        # 使用更严格的判断条件
        if sql.lower().startswith("select"):
            return self.select(sql, param, limit)
        else:
            return self.update(sql, param)

    def close(self):
        # 将连接返回到连接池，而不是关闭它
        self.db.close()
