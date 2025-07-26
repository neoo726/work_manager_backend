"""
数据库连接和操作模块
"""
import psycopg2
from psycopg2.extras import RealDictCursor
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
            'port': settings.db_port
        }
    
    def get_connection(self):
        """获取数据库连接"""
        try:
            conn = psycopg2.connect(**self.connection_params)
            return conn
        except psycopg2.Error as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    @contextmanager
    def get_db_connection(self) -> Generator[psycopg2.extensions.connection, None, None]:
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
    def get_db_cursor(self, dict_cursor: bool = True) -> Generator[psycopg2.extensions.cursor, None, None]:
        """获取数据库游标的上下文管理器"""
        with self.get_db_connection() as conn:
            cursor_factory = RealDictCursor if dict_cursor else None
            cursor = conn.cursor(cursor_factory=cursor_factory)
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
