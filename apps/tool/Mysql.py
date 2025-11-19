import pymysql
from flask import current_app
from config import current_config


class Mysql:
    def __init__(self, host=None, user=None, password=None, database=None, port=None):
        # 优先使用传入的参数，如果没有则使用配置文件中的配置
        self.host = host or getattr(current_config, 'DB_HOST', 'localhost')
        self.user = user or getattr(current_config, 'DB_USER', 'root')
        self.password = password or getattr(current_config, 'DB_PASSWORD', '123456')
        self.database = database or getattr(current_config, 'DB_NAME', 'music')
        self.port = port or getattr(current_config, 'DB_PORT', 3306)
        self.db = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            port=self.port,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def update(self, sql, param=()):
        sql = sql.strip()
        count = rowid = None
        cursor = self.db.cursor()
        try:
            # 修正：对于insert语句也使用execute，executemany用于批量插入
            # if sql.startswith("insert") and isinstance(param, tuple):
            #     count = cursor.executemany(sql, param)
            # else:
            #     count = cursor.execute(sql, param)
            
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
        self.db.close()
