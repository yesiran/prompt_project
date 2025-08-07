"""
路由模块初始化文件
作者: Claude
创建时间: 2025-08-06
功能: 注册所有路由蓝图
"""

from flask import Flask

def register_blueprints(app: Flask):
    """
    注册所有路由蓝图到Flask应用
    
    参数:
        app: Flask应用实例
    """
    # 导入并注册首页路由
    from app.routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    # 导入并注册Prompt编辑器路由
    from app.routes.prompt_editor import prompt_editor_bp
    app.register_blueprint(prompt_editor_bp)
    
    # TODO: 后续添加其他路由
    # from app.routes.auth import auth_bp
    # from app.routes.templates import templates_bp
    # from app.routes.activities import activities_bp
    # from app.routes.integrations import integrations_bp
    
    # app.register_blueprint(auth_bp)
    # app.register_blueprint(templates_bp)
    # app.register_blueprint(activities_bp)
    # app.register_blueprint(integrations_bp)