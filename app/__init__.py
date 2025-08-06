"""
Flask应用初始化模块
作者: Claude
创建时间: 2025-08-06
功能: 创建和配置Flask应用实例
"""

from flask import Flask
from app.config import Config, DevelopmentConfig, ProductionConfig
from app.common.logger import get_logger
import os

# 获取日志器
logger = get_logger(__name__)


def create_app(config_name: str = None) -> Flask:
    """
    创建Flask应用实例
    
    参数:
        config_name: 配置名称 ('development', 'production')，
                    如果为None，则从环境变量ENV读取
    
    返回:
        配置好的Flask应用实例
    """
    # 创建Flask实例
    app = Flask(__name__)
    
    # 确定配置类
    if config_name is None:
        config_name = os.getenv('ENV', 'development')
    
    # 选择配置类
    config_class = {
        'development': DevelopmentConfig,
        'production': ProductionConfig
    }.get(config_name, DevelopmentConfig)
    
    # 加载配置
    app.config.from_object(config_class())
    
    logger.info(f"Flask应用启动，环境: {config_name}")
    
    # 初始化扩展
    init_extensions(app)
    
    # 注册路由蓝图
    from app.routes import register_blueprints
    register_blueprints(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 注册模板过滤器
    register_template_filters(app)
    
    return app


def init_extensions(app: Flask):
    """
    初始化Flask扩展
    
    参数:
        app: Flask应用实例
    """
    # TODO: 初始化数据库
    # from app.common.database import db
    # db.init_app(app)
    
    # TODO: 初始化缓存
    # from app.common.cache import cache
    # cache.init_app(app)
    
    # TODO: 初始化CORS
    # from flask_cors import CORS
    # CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    logger.info("Flask扩展初始化完成")


def register_error_handlers(app: Flask):
    """
    注册错误处理器
    
    参数:
        app: Flask应用实例
    """
    from flask import send_from_directory
    import os
    
    @app.route('/favicon.ico')
    def favicon():
        """提供favicon图标"""
        return send_from_directory(
            os.path.join(app.root_path, 'static'),
            'favicon.svg',
            mimetype='image/svg+xml'
        )
    
    @app.errorhandler(404)
    def page_not_found(e):
        """处理404错误"""
        logger.warning(f"404错误: {e}")
        from flask import render_template
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        """处理500错误"""
        logger.error(f"500错误: {e}", exc_info=True)
        from flask import render_template
        return render_template('500.html'), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        """处理所有未捕获的异常"""
        logger.error(f"未捕获的异常: {e}", exc_info=True)
        from flask import jsonify, request
        
        # 如果是API请求，返回JSON
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': '服务器内部错误'
            }), 500
        
        # 否则返回错误页面
        from flask import render_template
        return render_template('500.html'), 500


def register_template_filters(app: Flask):
    """
    注册自定义模板过滤器
    
    参数:
        app: Flask应用实例
    """
    @app.template_filter('format_datetime')
    def format_datetime_filter(datetime_obj):
        """格式化日期时间"""
        if datetime_obj:
            return datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
        return ''
    
    @app.template_filter('truncate_text')
    def truncate_text_filter(text, length=100):
        """截断文本"""
        if text and len(text) > length:
            return text[:length] + '...'
        return text or ''