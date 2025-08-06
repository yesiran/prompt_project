"""
日志管理模块
支持debug和production两种模式，提供文件级别的持久化存储
日志按日期切分，错误日志单独存储
"""

import os
import sys
import logging
import traceback
from pathlib import Path
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
from typing import Optional, Dict, Any
import colorlog


class LoggerManager:
    """
    日志管理器
    负责创建和配置日志记录器，支持多环境切换
    """
    
    def __init__(self, config: Optional[Any] = None):
        """
        初始化日志管理器
        
        Args:
            config: 配置对象，如果不提供则使用默认配置
        """
        if config is None:
            # 如果没有提供配置，使用默认配置
            from app.config import config
            self.config = config
        else:
            self.config = config
        
        # 日志级别映射
        self.level_mapping = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        # 存储已创建的logger实例
        self.loggers: Dict[str, logging.Logger] = {}
        
        # 初始化根日志器
        self._setup_root_logger()
    
    def _setup_root_logger(self):
        """设置根日志器"""
        # 获取根日志器
        root_logger = logging.getLogger()
        root_logger.setLevel(self.level_mapping.get(self.config.LOG_LEVEL, logging.INFO))
        
        # 清除已有的处理器
        root_logger.handlers.clear()
        
        # 添加控制台处理器
        console_handler = self._create_console_handler()
        root_logger.addHandler(console_handler)
    
    def get_logger(self, name: str = 'app') -> logging.Logger:
        """
        获取或创建指定名称的日志器
        
        Args:
            name: 日志器名称，通常使用模块名
            
        Returns:
            logging.Logger: 配置好的日志器实例
        """
        # 如果已存在则直接返回
        if name in self.loggers:
            return self.loggers[name]
        
        # 创建新的日志器
        logger = logging.getLogger(name)
        logger.setLevel(self.level_mapping.get(self.config.LOG_LEVEL, logging.INFO))
        
        # 防止日志重复（不向上传播到根日志器）
        logger.propagate = False
        
        # 清除可能存在的旧处理器
        logger.handlers.clear()
        
        # 添加控制台处理器
        console_handler = self._create_console_handler()
        logger.addHandler(console_handler)
        
        # 添加文件处理器
        file_handler = self._create_file_handler(name)
        logger.addHandler(file_handler)
        
        # 添加错误日志单独处理器
        error_handler = self._create_error_handler(name)
        logger.addHandler(error_handler)
        
        # 缓存日志器实例
        self.loggers[name] = logger
        
        return logger
    
    def _create_console_handler(self) -> logging.Handler:
        """
        创建控制台处理器
        开发环境使用彩色输出，生产环境使用普通输出
        
        Returns:
            logging.Handler: 控制台处理器
        """
        if self.config.DEBUG:
            # 开发环境：使用彩色控制台输出
            console_handler = colorlog.StreamHandler(sys.stdout)
            
            # 彩色格式化器
            color_formatter = colorlog.ColoredFormatter(
                fmt='%(log_color)s[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s%(reset)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                }
            )
            console_handler.setFormatter(color_formatter)
        else:
            # 生产环境：使用普通控制台输出
            console_handler = logging.StreamHandler(sys.stdout)
            
            # 普通格式化器
            formatter = logging.Formatter(
                fmt='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(formatter)
        
        # 设置级别
        console_handler.setLevel(self.level_mapping.get(self.config.LOG_LEVEL, logging.INFO))
        
        return console_handler
    
    def _create_file_handler(self, logger_name: str) -> logging.Handler:
        """
        创建文件处理器，按日期切分日志文件
        
        Args:
            logger_name: 日志器名称
            
        Returns:
            logging.Handler: 文件处理器
        """
        # 构建日志文件路径
        # 格式：prompt_project_log.2024.12.01
        today = datetime.now().strftime('%Y.%m.%d')
        log_filename = f"prompt_project_log.{today}"
        log_path = self.config.LOG_DIR / log_filename
        
        # 创建按日期轮转的文件处理器
        # when='midnight' 表示每天午夜切分
        # interval=1 表示每1天切分一次
        # backupCount 表示保留的备份文件数量
        file_handler = TimedRotatingFileHandler(
            filename=str(log_path),
            when='midnight',
            interval=1,
            backupCount=self.config.LOG_RETENTION_DAYS,
            encoding='utf-8'
        )
        
        # 设置文件名后缀格式
        file_handler.suffix = ''  # 不添加额外后缀，我们已经在文件名中包含日期
        
        # 自定义文件名生成函数
        def custom_namer(default_name: str) -> str:
            """自定义日志文件命名"""
            # 获取日期部分
            base_name = os.path.basename(default_name)
            dir_name = os.path.dirname(default_name)
            
            # 如果是轮转的备份文件，修改命名格式
            if '.' in base_name and base_name.count('.') > 3:
                # 提取日期部分并重新格式化
                parts = base_name.split('.')
                if len(parts) >= 5:  # prompt_project_log.YYYY.MM.DD.timestamp
                    # 重构为我们想要的格式
                    date_str = f"{parts[1]}.{parts[2]}.{parts[3]}"
                    new_name = f"prompt_project_log.{date_str}"
                    return os.path.join(dir_name, new_name)
            
            return default_name
        
        file_handler.namer = custom_namer
        
        # 设置日志格式
        if self.config.DEBUG:
            # Debug模式：详细格式，包含文件名和行号
            formatter = logging.Formatter(
                fmt='[%(asctime)s] [%(name)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:
            # Production模式：标准格式
            formatter = logging.Formatter(
                fmt='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        file_handler.setFormatter(formatter)
        file_handler.setLevel(self.level_mapping.get(self.config.LOG_LEVEL, logging.INFO))
        
        return file_handler
    
    def _create_error_handler(self, logger_name: str) -> logging.Handler:
        """
        创建错误日志处理器，单独存储ERROR级别以上的日志
        
        Args:
            logger_name: 日志器名称
            
        Returns:
            logging.Handler: 错误日志处理器
        """
        # 构建错误日志文件路径
        today = datetime.now().strftime('%Y.%m.%d')
        error_filename = f"error.{today}"
        error_path = self.config.LOG_DIR / 'error' / error_filename
        
        # 创建按日期轮转的错误文件处理器
        error_handler = TimedRotatingFileHandler(
            filename=str(error_path),
            when='midnight',
            interval=1,
            backupCount=self.config.LOG_RETENTION_DAYS,
            encoding='utf-8'
        )
        
        # 自定义文件名生成函数
        def custom_error_namer(default_name: str) -> str:
            """自定义错误日志文件命名"""
            base_name = os.path.basename(default_name)
            dir_name = os.path.dirname(default_name)
            
            if '.' in base_name and base_name.count('.') > 3:
                parts = base_name.split('.')
                if len(parts) >= 4:
                    date_str = f"{parts[1]}.{parts[2]}.{parts[3]}"
                    new_name = f"error.{date_str}"
                    return os.path.join(dir_name, new_name)
            
            return default_name
        
        error_handler.namer = custom_error_namer
        
        # 设置详细的错误日志格式
        error_formatter = logging.Formatter(
            fmt='[%(asctime)s] [%(name)s] [%(levelname)s] [%(filename)s:%(lineno)d]\n'
                '%(message)s\n'
                '----------------------------------------',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        error_handler.setFormatter(error_formatter)
        # 只记录ERROR级别及以上的日志
        error_handler.setLevel(logging.ERROR)
        
        return error_handler
    
    def log_exception(self, logger_name: str = 'app', exc_info: Optional[tuple] = None):
        """
        记录异常信息，包含完整的堆栈跟踪
        
        Args:
            logger_name: 日志器名称
            exc_info: 异常信息元组，如果不提供则获取当前异常
        """
        logger = self.get_logger(logger_name)
        
        if exc_info is None:
            exc_info = sys.exc_info()
        
        # 获取完整的异常堆栈
        exc_type, exc_value, exc_traceback = exc_info
        
        if exc_type is not None:
            # 格式化异常信息
            tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            tb_text = ''.join(tb_lines)
            
            # 记录异常
            logger.error(f"Exception occurred:\n{tb_text}")
    
    def cleanup_old_logs(self):
        """
        清理过期的日志文件
        根据配置的保留天数删除旧日志
        """
        logger = self.get_logger('logger_manager')
        
        try:
            retention_days = self.config.LOG_RETENTION_DAYS
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            # 清理主日志目录
            for log_file in self.config.LOG_DIR.glob('prompt_project_log.*'):
                # 解析文件名中的日期
                try:
                    date_str = log_file.name.replace('prompt_project_log.', '')
                    file_date = datetime.strptime(date_str, '%Y.%m.%d')
                    
                    if file_date < cutoff_date:
                        log_file.unlink()
                        logger.info(f"删除过期日志文件: {log_file.name}")
                except (ValueError, OSError) as e:
                    logger.warning(f"处理日志文件时出错 {log_file.name}: {e}")
            
            # 清理错误日志目录
            error_dir = self.config.LOG_DIR / 'error'
            if error_dir.exists():
                for error_file in error_dir.glob('error.*'):
                    try:
                        date_str = error_file.name.replace('error.', '')
                        file_date = datetime.strptime(date_str, '%Y.%m.%d')
                        
                        if file_date < cutoff_date:
                            error_file.unlink()
                            logger.info(f"删除过期错误日志文件: {error_file.name}")
                    except (ValueError, OSError) as e:
                        logger.warning(f"处理错误日志文件时出错 {error_file.name}: {e}")
        
        except Exception as e:
            logger.error(f"清理日志文件时发生错误: {e}")


# 创建全局日志管理器实例
logger_manager = LoggerManager()


def get_logger(name: str = 'app') -> logging.Logger:
    """
    获取日志器的便捷函数
    
    Args:
        name: 日志器名称
        
    Returns:
        logging.Logger: 配置好的日志器实例
    """
    return logger_manager.get_logger(name)


def log_function_call(func):
    """
    装饰器：记录函数调用
    在DEBUG模式下记录函数的调用参数和返回值
    
    Args:
        func: 要装饰的函数
        
    Returns:
        包装后的函数
    """
    def wrapper(*args, **kwargs):
        """
        装饰器包装函数
        *args: 位置参数元组
        **kwargs: 关键字参数字典
        """
        logger = get_logger(func.__module__)
        
        # 只在DEBUG模式下记录
        if logger.level == logging.DEBUG:
            # 记录函数调用
            func_name = func.__name__
            logger.debug(f"调用函数 {func_name}")
            logger.debug(f"  参数: args={args}, kwargs={kwargs}")
            
            try:
                # 执行函数
                result = func(*args, **kwargs)
                logger.debug(f"  返回: {result}")
                return result
            except Exception as e:
                logger.error(f"  函数 {func_name} 执行出错: {e}")
                raise
        else:
            # 非DEBUG模式直接执行
            return func(*args, **kwargs)
    
    return wrapper


def log_performance(func):
    """
    装饰器：记录函数性能
    记录函数执行时间
    
    Args:
        func: 要装饰的函数
        
    Returns:
        包装后的函数
    """
    import time
    
    def wrapper(*args, **kwargs):
        """
        装饰器包装函数
        *args: 位置参数元组
        **kwargs: 关键字参数字典
        """
        logger = get_logger(func.__module__)
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            
            # 如果执行时间超过1秒，记录警告
            if elapsed_time > 1.0:
                logger.warning(f"函数 {func.__name__} 执行时间过长: {elapsed_time:.2f}秒")
            elif logger.level == logging.DEBUG:
                logger.debug(f"函数 {func.__name__} 执行时间: {elapsed_time:.3f}秒")
            
            return result
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"函数 {func.__name__} 执行失败 (耗时{elapsed_time:.2f}秒): {e}")
            raise
    
    return wrapper