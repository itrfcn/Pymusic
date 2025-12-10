#!/usr/bin/env python3
"""
用于在user表中添加is_admin字段的脚本
"""

from apps.tool.Mysql import Mysql


def main():
    try:
        with Mysql() as mysql:
            # 检查is_admin字段是否已存在
            check_sql = "SHOW COLUMNS FROM user LIKE 'is_admin'"
            result = mysql.sql(check_sql)
            
            if not result:
                # 字段不存在，添加字段
                alter_sql = "ALTER TABLE user ADD COLUMN is_admin TINYINT(1) DEFAULT 0 NOT NULL"
                result = mysql.sql(alter_sql)
                print(f"添加is_admin字段成功: {result}")
            else:
                print("is_admin字段已存在，无需添加")
                print(f"字段信息: {result[0]}")
    except Exception as e:
        print(f"执行出错: {e}")


if __name__ == "__main__":
    main()