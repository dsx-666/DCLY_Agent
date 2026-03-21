import psycopg2
from psycopg2 import OperationalError, ProgrammingError
from typing import List, Dict, Tuple, Optional
import json
SQL_HOST = "111778qb4bq84.vicp.fun"
SQL_PORT = 17769
SQL_PASSWORD = "lml20050523"
DATABASES = "agent_project"
# 数据库连接配置（替换为你的实际信息）
DB_CONFIG = {
    "host": SQL_HOST,  # 主机
    "port": SQL_PORT,                     # 端口
    "user": "postgreRoot",             # 数据库用户名
    "password": SQL_PASSWORD,       # 数据库密码
    "database": DATABASES             # 数据库名
}

def get_db_connection() -> Optional[psycopg2.extensions.connection]:
    """
    获取数据库连接对象
    :return: 数据库连接对象 | None
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True  # 自动提交事务，避免锁表
        conn.set_client_encoding('utf8')  # 确保中文注释正常显示
        return conn
    except OperationalError as e:
        # print(f"数据库连接失败：{str(e)}")
        return None

conn = get_db_connection()



