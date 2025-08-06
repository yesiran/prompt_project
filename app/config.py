"""
应用配置管理模块
负责从环境变量加载配置，提供全局配置访问接口
支持开发环境和生产环境的配置切换
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv


class Config:
    """
    配置基类
    定义所有环境通用的配置项
    """
    
    def __init__(self):
        """初始化配置，从.env文件加载环境变量"""
        # 获取项目根目录路径
        self.BASE_DIR = Path(__file__).parent.parent
        
        # 加载.env文件
        env_file = self.BASE_DIR / '.env'
        if env_file.exists():
            load_dotenv(env_file)
        else:
            # 如果.env不存在，尝试加载.env.template作为默认配置
            template_file = self.BASE_DIR / '.env.template'
            if template_file.exists():
                load_dotenv(template_file)
        
        # ============== 环境设置 ==============
        self.ENV = os.getenv('ENV', 'development')
        self.DEBUG = self.ENV == 'development'
        self.TESTING = False
        self.SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-please-change')
        
        # ============== 数据库配置 ==============
        self.DB_HOST = os.getenv('DB_HOST', 'localhost')
        self.DB_PORT = int(os.getenv('DB_PORT', 3306))
        self.DB_USER = os.getenv('DB_USER', 'root')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD', '')
        self.DB_NAME = os.getenv('DB_NAME', 'prompt_db')
        self.DB_CHARSET = os.getenv('DB_CHARSET', 'utf8mb4')
        
        # 数据库连接池配置
        self.DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', 5))
        self.DB_POOL_RECYCLE = int(os.getenv('DB_POOL_RECYCLE', 3600))
        self.DB_POOL_TIMEOUT = int(os.getenv('DB_POOL_TIMEOUT', 30))
        self.DB_MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', 10))
        
        # 构建数据库URI
        self.DATABASE_URI = self._build_database_uri()
        
        # ============== 日志配置 ==============
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG' if self.DEBUG else 'INFO')
        self.LOG_DIR = self.BASE_DIR / os.getenv('LOG_DIR', 'logs')
        self.LOG_MAX_SIZE = int(os.getenv('LOG_MAX_SIZE', 100)) * 1024 * 1024  # 转换为字节
        self.LOG_RETENTION_DAYS = int(os.getenv('LOG_RETENTION_DAYS', 30))
        
        # 确保日志目录存在
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
        (self.LOG_DIR / 'error').mkdir(exist_ok=True)
        
        # ============== 服务器配置 ==============
        self.APP_HOST = os.getenv('APP_HOST', '0.0.0.0')
        self.APP_PORT = int(os.getenv('APP_PORT', 5000))
        self.WORKERS = int(os.getenv('WORKERS', 1))
        
        # ============== API密钥配置 ==============
        # OpenAI配置
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
        self.OPENAI_API_BASE = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        self.OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
        
        # Claude配置
        self.CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY', '')
        self.CLAUDE_API_BASE = os.getenv('CLAUDE_API_BASE', 'https://api.anthropic.com')
        self.CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3')
        
        # 文心一言配置
        self.WENXIN_API_KEY = os.getenv('WENXIN_API_KEY', '')
        self.WENXIN_SECRET_KEY = os.getenv('WENXIN_SECRET_KEY', '')
        self.WENXIN_API_BASE = os.getenv('WENXIN_API_BASE', 'https://aip.baidubce.com')
        
        # ============== 缓存配置 ==============
        self.REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
        self.REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
        self.REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
        self.REDIS_DB = int(os.getenv('REDIS_DB', 0))
        self.CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 300))
        
        # ============== 安全配置 ==============
        self.CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
        self.SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))
        self.RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 60))
        
        # ============== 其他配置 ==============
        self.TIMEZONE = os.getenv('TIMEZONE', 'Asia/Shanghai')
        self.PAGE_SIZE = int(os.getenv('PAGE_SIZE', 20))
        self.MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', 10)) * 1024 * 1024  # 转换为字节
    
    def _build_database_uri(self) -> str:
        """
        构建数据库连接URI
        
        Returns:
            str: MySQL数据库连接字符串
        """
        # 构建MySQL连接字符串
        # 格式: mysql+pymysql://user:password@host:port/database?charset=utf8mb4
        uri = (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?charset={self.DB_CHARSET}"
        )
        return uri
    
    def get_api_config(self, provider: str) -> Dict[str, Any]:
        """
        获取指定AI提供商的API配置
        
        Args:
            provider: API提供商名称 ('openai', 'claude', 'wenxin')
            
        Returns:
            dict: API配置字典
        """
        provider = provider.lower()
        
        if provider == 'openai':
            return {
                'api_key': self.OPENAI_API_KEY,
                'api_base': self.OPENAI_API_BASE,
                'model': self.OPENAI_MODEL,
                'enabled': bool(self.OPENAI_API_KEY)
            }
        elif provider == 'claude':
            return {
                'api_key': self.CLAUDE_API_KEY,
                'api_base': self.CLAUDE_API_BASE,
                'model': self.CLAUDE_MODEL,
                'enabled': bool(self.CLAUDE_API_KEY)
            }
        elif provider == 'wenxin':
            return {
                'api_key': self.WENXIN_API_KEY,
                'secret_key': self.WENXIN_SECRET_KEY,
                'api_base': self.WENXIN_API_BASE,
                'enabled': bool(self.WENXIN_API_KEY and self.WENXIN_SECRET_KEY)
            }
        else:
            return {'enabled': False}
    
    def validate(self) -> tuple[bool, list[str]]:
        """
        验证配置的完整性和有效性
        
        Returns:
            tuple: (是否有效, 错误信息列表)
        """
        errors = []
        
        # 检查必要的配置项
        if not self.SECRET_KEY or self.SECRET_KEY == 'your-secret-key-here-change-in-production':
            errors.append("SECRET_KEY未配置或使用了默认值，请在生产环境中设置安全的密钥")
        
        if not self.DB_PASSWORD and self.ENV == 'production':
            errors.append("生产环境中数据库密码不能为空")
        
        if not self.DB_NAME:
            errors.append("数据库名称未配置")
        
        # 检查至少有一个API配置
        api_configured = any([
            self.get_api_config('openai')['enabled'],
            self.get_api_config('claude')['enabled'],
            self.get_api_config('wenxin')['enabled']
        ])
        
        if not api_configured:
            errors.append("警告：没有配置任何AI API密钥，部分功能将不可用")
        
        return len(errors) == 0, errors
    
    def __repr__(self) -> str:
        """返回配置的字符串表示"""
        return f"<Config ENV={self.ENV} DEBUG={self.DEBUG}>"


class DevelopmentConfig(Config):
    """开发环境配置"""
    
    def __init__(self):
        super().__init__()
        self.ENV = 'development'
        self.DEBUG = True
        self.LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """生产环境配置"""
    
    def __init__(self):
        super().__init__()
        self.ENV = 'production'
        self.DEBUG = False
        self.LOG_LEVEL = 'INFO'
        # 生产环境强制关闭调试模式
        os.environ['FLASK_DEBUG'] = 'False'


# 配置映射字典
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(env: Optional[str] = None) -> Config:
    """
    获取配置实例
    
    Args:
        env: 环境名称，如果不指定则从环境变量读取
        
    Returns:
        Config: 配置实例
    """
    if env is None:
        env = os.getenv('ENV', 'development')
    
    config_class = config_dict.get(env, DevelopmentConfig)
    return config_class()


# 创建全局配置实例
config = get_config()