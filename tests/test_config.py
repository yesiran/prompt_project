"""
配置模块单元测试
测试配置加载、环境切换、配置验证等功能
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import Config, DevelopmentConfig, ProductionConfig, get_config


def test_config_initialization():
    """测试配置初始化"""
    config = Config()
    
    # 测试基础配置项是否存在
    assert hasattr(config, 'ENV')
    assert hasattr(config, 'DEBUG')
    assert hasattr(config, 'SECRET_KEY')
    assert hasattr(config, 'DATABASE_URI')
    assert hasattr(config, 'LOG_DIR')
    
    print("✓ 配置初始化测试通过")


def test_development_config():
    """测试开发环境配置"""
    config = DevelopmentConfig()
    
    assert config.ENV == 'development'
    assert config.DEBUG == True
    assert config.LOG_LEVEL == 'DEBUG'
    
    print("✓ 开发环境配置测试通过")


def test_production_config():
    """测试生产环境配置"""
    config = ProductionConfig()
    
    assert config.ENV == 'production'
    assert config.DEBUG == False
    assert config.LOG_LEVEL == 'INFO'
    
    print("✓ 生产环境配置测试通过")


def test_database_uri_build():
    """测试数据库URI构建"""
    config = Config()
    
    # 测试URI格式是否正确
    assert 'mysql+pymysql://' in config.DATABASE_URI
    assert config.DB_NAME in config.DATABASE_URI
    assert f'charset={config.DB_CHARSET}' in config.DATABASE_URI
    
    print(f"✓ 数据库URI构建测试通过: {config.DATABASE_URI}")


def test_api_config_retrieval():
    """测试API配置获取"""
    config = Config()
    
    # 测试OpenAI配置
    openai_config = config.get_api_config('openai')
    assert 'api_key' in openai_config
    assert 'api_base' in openai_config
    assert 'model' in openai_config
    assert 'enabled' in openai_config
    
    # 测试Claude配置
    claude_config = config.get_api_config('claude')
    assert 'api_key' in claude_config
    assert 'api_base' in claude_config
    assert 'model' in claude_config
    assert 'enabled' in claude_config
    
    # 测试文心一言配置
    wenxin_config = config.get_api_config('wenxin')
    assert 'api_key' in wenxin_config
    assert 'secret_key' in wenxin_config
    assert 'api_base' in wenxin_config
    assert 'enabled' in wenxin_config
    
    # 测试不存在的提供商
    unknown_config = config.get_api_config('unknown')
    assert unknown_config == {'enabled': False}
    
    print("✓ API配置获取测试通过")


def test_config_validation():
    """测试配置验证"""
    config = Config()
    
    # 执行验证
    is_valid, errors = config.validate()
    
    # 验证返回值格式
    assert isinstance(is_valid, bool)
    assert isinstance(errors, list)
    
    # 打印验证结果
    if errors:
        print("配置验证警告/错误:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ 配置验证测试通过，无错误")


def test_environment_switching():
    """测试环境切换"""
    # 测试默认环境
    config_default = get_config()
    assert config_default.ENV in ['development', 'production']
    
    # 测试指定开发环境
    config_dev = get_config('development')
    assert config_dev.ENV == 'development'
    assert config_dev.DEBUG == True
    
    # 测试指定生产环境
    config_prod = get_config('production')
    assert config_prod.ENV == 'production'
    assert config_prod.DEBUG == False
    
    print("✓ 环境切换测试通过")


def test_path_configurations():
    """测试路径配置"""
    config = Config()
    
    # 测试BASE_DIR是否正确
    assert config.BASE_DIR.exists()
    assert (config.BASE_DIR / 'app').exists()
    
    # 测试日志目录是否创建
    assert config.LOG_DIR.exists()
    assert (config.LOG_DIR / 'error').exists()
    
    print(f"✓ 路径配置测试通过")
    print(f"  - 项目根目录: {config.BASE_DIR}")
    print(f"  - 日志目录: {config.LOG_DIR}")


def test_size_conversions():
    """测试大小单位转换"""
    config = Config()
    
    # 测试日志文件大小转换（MB到字节）
    log_max_size_mb = int(os.getenv('LOG_MAX_SIZE', 100))
    assert config.LOG_MAX_SIZE == log_max_size_mb * 1024 * 1024
    
    # 测试上传文件大小转换（MB到字节）
    max_upload_mb = int(os.getenv('MAX_UPLOAD_SIZE', 10))
    assert config.MAX_UPLOAD_SIZE == max_upload_mb * 1024 * 1024
    
    print("✓ 大小单位转换测试通过")


if __name__ == '__main__':
    print("=" * 50)
    print("开始执行配置模块单元测试")
    print("=" * 50)
    
    test_config_initialization()
    test_development_config()
    test_production_config()
    test_database_uri_build()
    test_api_config_retrieval()
    test_config_validation()
    test_environment_switching()
    test_path_configurations()
    test_size_conversions()
    
    print("=" * 50)
    print("所有配置模块测试完成！")
    print("=" * 50)