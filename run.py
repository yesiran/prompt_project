#!/usr/bin/env python3
"""
应用启动入口
作者: Claude
创建时间: 2025-08-06
功能: Flask应用的启动脚本
"""

import os
import sys
from pathlib import Path

# 将项目根目录添加到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app
from app.common.logger import get_logger

# 获取日志器
logger = get_logger(__name__)


def main():
    """
    主函数
    创建并运行Flask应用
    """
    # 从环境变量获取配置
    env = os.getenv('ENV', 'development')
    port = int(os.getenv('FLASK_PORT', 5001))
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    
    # 创建应用实例
    app = create_app(env)
    
    # 打印启动信息
    logger.info(f"========================================")
    logger.info(f"Prompt管理系统启动")
    logger.info(f"环境: {env}")
    logger.info(f"地址: http://{host}:{port}")
    logger.info(f"========================================")
    
    # 运行应用
    if env == 'development':
        # 开发环境使用Flask内置服务器
        app.run(
            host=host,
            port=port,
            debug=True,
            use_reloader=True
        )
    else:
        # 生产环境应该使用WSGI服务器（如Gunicorn）
        logger.warning("生产环境请使用Gunicorn等WSGI服务器运行")
        app.run(
            host=host,
            port=port,
            debug=False
        )


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("应用被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"应用启动失败: {str(e)}", exc_info=True)
        sys.exit(1)
