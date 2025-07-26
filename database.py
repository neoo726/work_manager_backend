"""
数据库连接和操作模块
"""
import pymysql
from contextlib import contextmanager
from typing import Generator, Optional
import logging
from config import settings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理器"""

    def __init__(self):
        self.connection_params = {
            'host': settings.db_host,
            'database': settings.db_name,
            'user': settings.db_user,
            'password': settings.db_password,
            'port': settings.db_port,
            'charset': 'utf8mb4',
            'autocommit': False
        }

    def get_connection(self):
        """获取数据库连接"""
        try:
            conn = pymysql.connect(**self.connection_params)
            return conn
        except pymysql.Error as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    @contextmanager
    def get_db_connection(self) -> Generator[pymysql.Connection, None, None]:
        """获取数据库连接的上下文管理器"""
        conn = None
        try:
            conn = self.get_connection()
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            if conn:
                conn.close()

    @contextmanager
    def get_db_cursor(self, dict_cursor: bool = True) -> Generator[pymysql.cursors.Cursor, None, None]:
        """获取数据库游标的上下文管理器"""
        with self.get_db_connection() as conn:
            cursor_class = pymysql.cursors.DictCursor if dict_cursor else pymysql.cursors.Cursor
            cursor = conn.cursor(cursor_class)
            try:
                yield cursor
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"数据库操作失败: {e}")
                raise
            finally:
                cursor.close()
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    return result is not None
        except Exception as e:
            logger.error(f"数据库连接测试失败: {e}")
            return False


# 全局数据库管理器实例
db_manager = DatabaseManager()


def get_db_manager() -> DatabaseManager:
    """获取数据库管理器实例"""
    return db_manager
