"""
日志模块单元测试
测试日志记录、文件输出、错误处理等功能
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
import time

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.common.logger import (
    LoggerManager, 
    get_logger, 
    log_function_call, 
    log_performance
)
from app.config import get_config


def test_logger_creation():
    """测试日志器创建"""
    # 获取日志器
    logger = get_logger('test_module')
    
    # 验证日志器存在
    assert logger is not None
    assert logger.name == 'test_module'
    assert isinstance(logger, logging.Logger)
    
    print("✓ 日志器创建测试通过")


def test_logger_singleton():
    """测试日志器单例模式"""
    # 多次获取同一个日志器
    logger1 = get_logger('test_singleton')
    logger2 = get_logger('test_singleton')
    
    # 应该是同一个实例
    assert logger1 is logger2
    
    print("✓ 日志器单例模式测试通过")


def test_log_levels():
    """测试不同日志级别"""
    logger = get_logger('test_levels')
    
    # 测试各个级别的日志记录
    try:
        logger.debug("这是DEBUG级别日志")
        logger.info("这是INFO级别日志")
        logger.warning("这是WARNING级别日志")
        logger.error("这是ERROR级别日志")
        logger.critical("这是CRITICAL级别日志")
        
        print("✓ 日志级别测试通过")
    except Exception as e:
        print(f"✗ 日志级别测试失败: {e}")
        raise


def test_log_file_creation():
    """测试日志文件创建"""
    config = get_config()
    logger = get_logger('test_file')
    
    # 记录一条日志
    logger.info("测试日志文件创建")
    
    # 检查日志文件是否创建
    today = datetime.now().strftime('%Y.%m.%d')
    log_file = config.LOG_DIR / f"prompt_project_log.{today}"
    
    # 给文件系统一点时间
    time.sleep(0.1)
    
    # 验证文件存在
    assert log_file.exists(), f"日志文件不存在: {log_file}"
    
    print(f"✓ 日志文件创建测试通过: {log_file}")


def test_error_log_separation():
    """测试错误日志单独存储"""
    config = get_config()
    logger = get_logger('test_error')
    
    # 记录错误日志
    logger.error("这是一个测试错误")
    
    # 检查错误日志文件
    today = datetime.now().strftime('%Y.%m.%d')
    error_file = config.LOG_DIR / 'error' / f"error.{today}"
    
    # 给文件系统一点时间
    time.sleep(0.1)
    
    # 验证错误文件存在
    assert error_file.exists(), f"错误日志文件不存在: {error_file}"
    
    print(f"✓ 错误日志分离测试通过: {error_file}")


def test_exception_logging():
    """测试异常日志记录"""
    logger_manager = LoggerManager()
    logger = get_logger('test_exception')
    
    try:
        # 故意触发一个异常
        result = 1 / 0
    except ZeroDivisionError:
        # 记录异常
        logger_manager.log_exception('test_exception')
    
    print("✓ 异常日志记录测试通过")


def test_log_format():
    """测试日志格式"""
    logger = get_logger('test_format')
    
    # 记录一条日志
    test_message = "测试日志格式"
    logger.info(test_message)
    
    # 读取日志文件验证格式
    config = get_config()
    today = datetime.now().strftime('%Y.%m.%d')
    log_file = config.LOG_DIR / f"prompt_project_log.{today}"
    
    time.sleep(0.1)
    
    if log_file.exists():
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # 验证日志包含必要的元素
            assert 'test_format' in content  # 日志器名称
            assert test_message in content   # 日志消息
            assert '[INFO]' in content       # 日志级别
    
    print("✓ 日志格式测试通过")


@log_function_call
def test_function_with_decorator(x: int, y: int) -> int:
    """测试带装饰器的函数"""
    return x + y


def test_function_call_decorator():
    """测试函数调用装饰器"""
    # 设置日志级别为DEBUG以启用函数调用记录
    logger = get_logger(__name__)
    original_level = logger.level
    logger.setLevel(logging.DEBUG)
    
    # 调用被装饰的函数
    result = test_function_with_decorator(3, 5)
    assert result == 8
    
    # 恢复原始日志级别
    logger.setLevel(original_level)
    
    print("✓ 函数调用装饰器测试通过")


@log_performance
def slow_function():
    """模拟慢速函数"""
    time.sleep(0.1)
    return "完成"


def test_performance_decorator():
    """测试性能记录装饰器"""
    # 调用被装饰的函数
    result = slow_function()
    assert result == "完成"
    
    print("✓ 性能记录装饰器测试通过")


def test_logger_in_different_environments():
    """测试不同环境下的日志器行为"""
    # 测试开发环境
    dev_config = get_config('development')
    dev_logger_manager = LoggerManager(dev_config)
    dev_logger = dev_logger_manager.get_logger('test_dev')
    
    assert dev_logger.level == logging.DEBUG
    
    # 测试生产环境
    prod_config = get_config('production')
    prod_logger_manager = LoggerManager(prod_config)
    prod_logger = prod_logger_manager.get_logger('test_prod')
    
    assert prod_logger.level == logging.INFO
    
    print("✓ 多环境日志器测试通过")


def test_log_cleanup():
    """测试日志清理功能"""
    logger_manager = LoggerManager()
    
    try:
        # 执行清理（不会删除今天的日志）
        logger_manager.cleanup_old_logs()
        print("✓ 日志清理功能测试通过（执行无错误）")
    except Exception as e:
        print(f"✗ 日志清理功能测试失败: {e}")
        raise


if __name__ == '__main__':
    print("=" * 50)
    print("开始执行日志模块单元测试")
    print("=" * 50)
    
    test_logger_creation()
    test_logger_singleton()
    test_log_levels()
    test_log_file_creation()
    test_error_log_separation()
    test_exception_logging()
    test_log_format()
    test_function_call_decorator()
    test_performance_decorator()
    test_logger_in_different_environments()
    test_log_cleanup()
    
    print("=" * 50)
    print("所有日志模块测试完成！")
    print("=" * 50)
    print("\n提示：")
    print("1. 请检查 logs/ 目录下是否生成了日志文件")
    print("2. 请检查 logs/error/ 目录下是否生成了错误日志文件")
    print("3. 日志文件名格式应为: prompt_project_log.YYYY.MM.DD")