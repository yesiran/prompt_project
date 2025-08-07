"""
数据库连接管理模块
提供MySQL数据库连接池和基础操作封装
"""
import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager
from dbutils.pooled_db import PooledDB
from typing import Optional, Dict, Any, List
from app.config import config
from app.common.logger import get_logger

logger = get_logger(__name__)

# 数据库连接池实例
_db_pool: Optional[PooledDB] = None


def init_db_pool():
    """
    初始化数据库连接池
    """
    global _db_pool
    
    try:
        _db_pool = PooledDB(
            creator=pymysql,                    # 使用pymysql
            maxconnections=6,                   # 连接池允许的最大连接数
            mincached=2,                        # 初始化时创建的空闲连接数
            maxcached=config.DB_POOL_SIZE,     # 连接池中最多空闲的连接数
            maxusage=None,                      # 单个连接的最大重复使用次数
            blocking=True,                      # 连接池中如果没有可用连接是否阻塞等待
            setsession=[],                      # 开始会话前执行的SQL列表
            ping=0,                            # ping MySQL服务端，检查连接是否可用
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            charset=config.DB_CHARSET,
            cursorclass=DictCursor,            # 返回字典格式的结果
            autocommit=False                    # 关闭自动提交
        )
        logger.info(f"数据库连接池初始化成功: {config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}")
    except Exception as e:
        logger.error(f"数据库连接池初始化失败: {str(e)}", exc_info=True)
        raise


def get_db_pool() -> PooledDB:
    """
    获取数据库连接池实例
    
    Returns:
        PooledDB: 数据库连接池
    """
    global _db_pool
    if _db_pool is None:
        init_db_pool()
    return _db_pool


@contextmanager
def get_db_connection():
    """
    获取数据库连接上下文管理器
    使用with语句自动管理连接的获取和释放
    
    Example:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users")
                result = cursor.fetchall()
    """
    conn = None
    try:
        pool = get_db_pool()
        conn = pool.connection()
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"数据库操作失败: {str(e)}", exc_info=True)
        raise
    finally:
        if conn:
            conn.close()


class Database:
    """
    数据库操作封装类
    提供常用的数据库操作方法
    """
    
    @staticmethod
    def execute(sql: str, params: tuple = None, commit: bool = True) -> int:
        """
        执行SQL语句（INSERT/UPDATE/DELETE）
        
        Args:
            sql: SQL语句
            params: 参数元组
            commit: 是否提交事务
            
        Returns:
            int: 影响的行数
        """
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                if commit:
                    conn.commit()
                return cursor.rowcount
    
    @staticmethod
    def execute_many(sql: str, params_list: List[tuple], commit: bool = True) -> int:
        """
        批量执行SQL语句
        
        Args:
            sql: SQL语句
            params_list: 参数列表
            commit: 是否提交事务
            
        Returns:
            int: 影响的总行数
        """
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.executemany(sql, params_list)
                if commit:
                    conn.commit()
                return cursor.rowcount
    
    @staticmethod
    def insert(sql: str, params: tuple = None) -> int:
        """
        执行INSERT语句并返回插入的ID
        
        Args:
            sql: INSERT SQL语句
            params: 参数元组
            
        Returns:
            int: 插入记录的ID
        """
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                conn.commit()
                return cursor.lastrowid
    
    @staticmethod
    def select_one(sql: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """
        查询单条记录
        
        Args:
            sql: SELECT SQL语句
            params: 参数元组
            
        Returns:
            dict: 查询结果，如果没有则返回None
        """
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchone()
    
    @staticmethod
    def select_all(sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        查询多条记录
        
        Args:
            sql: SELECT SQL语句
            params: 参数元组
            
        Returns:
            list: 查询结果列表
        """
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()
    
    @staticmethod
    def select_page(sql: str, params: tuple = None, page: int = 1, 
                   page_size: int = 20) -> Dict[str, Any]:
        """
        分页查询
        
        Args:
            sql: SELECT SQL语句（不包含LIMIT）
            params: 参数元组
            page: 页码（从1开始）
            page_size: 每页大小
            
        Returns:
            dict: 包含数据和分页信息的字典
        """
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 查询总数
        count_sql = f"SELECT COUNT(*) as total FROM ({sql}) as t"
        total = Database.select_one(count_sql, params)['total']
        
        # 查询数据
        data_sql = f"{sql} LIMIT %s OFFSET %s"
        params = params + (page_size, offset) if params else (page_size, offset)
        data = Database.select_all(data_sql, params)
        
        # 计算总页数
        total_pages = (total + page_size - 1) // page_size
        
        return {
            'data': data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }
    
    @staticmethod
    def transaction(func):
        """
        事务装饰器
        被装饰的函数第一个参数必须是conn（数据库连接）
        
        Example:
            @Database.transaction
            def transfer_money(conn, from_id, to_id, amount):
                cursor = conn.cursor()
                # 扣款
                cursor.execute("UPDATE accounts SET balance = balance - %s WHERE id = %s", 
                             (amount, from_id))
                # 加款
                cursor.execute("UPDATE accounts SET balance = balance + %s WHERE id = %s", 
                             (amount, to_id))
        """
        def wrapper(*args, **kwargs):
            with get_db_connection() as conn:
                try:
                    result = func(conn, *args[1:], **kwargs)
                    conn.commit()
                    return result
                except Exception as e:
                    conn.rollback()
                    logger.error(f"事务执行失败: {str(e)}", exc_info=True)
                    raise
        return wrapper


# 初始化数据库连接池
def init_database():
    """
    初始化数据库
    检查数据库连接并创建必要的表
    """
    try:
        # 初始化连接池
        init_db_pool()
        
        # 测试连接
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result:
                    logger.info("数据库连接测试成功")
                    
        return True
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}", exc_info=True)
        return False


# 关闭数据库连接池
def close_database():
    """
    关闭数据库连接池
    """
    global _db_pool
    if _db_pool:
        _db_pool.close()
        _db_pool = None
        logger.info("数据库连接池已关闭")