"""
首页路由模块
作者: Claude
创建时间: 2025-08-06
功能: 处理首页相关的所有HTTP请求
"""

from flask import Blueprint, render_template, jsonify, request
from datetime import datetime
import logging

# 导入服务层
from app.services.dashboard_service import DashboardService
from app.common.logger import get_logger

# 创建蓝图
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/')

# 获取日志器
logger = get_logger(__name__)

# 创建服务实例
dashboard_service = DashboardService()


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
def index():
    """
    首页视图
    渲染首页HTML模板
    
    返回:
        渲染后的HTML页面
    """
    try:
        logger.info("访问首页")
        
        # 设置当前激活的页面（用于侧边栏高亮）
        active_page = 'dashboard'
        
        # 渲染模板
        return render_template('dashboard.html', active_page=active_page)
        
    except Exception as e:
        logger.error(f"渲染首页失败: {str(e)}", exc_info=True)
        return render_template('error.html', error="页面加载失败"), 500


@dashboard_bp.route('/api/dashboard/data')
def get_dashboard_data():
    """
    获取首页数据API
    返回首页所需的所有数据
    
    返回:
        JSON格式的首页数据
    """
    try:
        logger.info("获取首页数据")
        
        # 从服务层获取数据
        data = dashboard_service.get_dashboard_data()
        
        return jsonify({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        logger.error(f"获取首页数据失败: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': '获取数据失败'
        }), 500


@dashboard_bp.route('/api/user/greeting')
def get_greeting():
    """
    获取个性化问候语API
    根据当前时间返回合适的问候语
    
    返回:
        JSON格式的问候信息
    """
    try:
        current_hour = datetime.now().hour
        
        # 根据时间确定问候语
        if 5 <= current_hour < 12:
            time_of_day = 'morning'
            greeting = '早上好'
        elif 12 <= current_hour < 18:
            time_of_day = 'afternoon'
            greeting = '下午好'
        elif 18 <= current_hour < 22:
            time_of_day = 'evening'
            greeting = '晚上好'
        else:
            time_of_day = 'night'
            greeting = '夜深了'
        
        # 获取用户信息（暂时使用模拟数据）
        user_data = dashboard_service.get_user_greeting_data()
        
        return jsonify({
            'success': True,
            'data': {
                'timeOfDay': time_of_day,
                'greeting': greeting,
                'userName': user_data.get('userName', '用户'),
                'todayTaskCount': user_data.get('todayTaskCount', 0),
                'pendingPrompts': user_data.get('pendingPrompts', 0)
            }
        })
        
    except Exception as e:
        logger.error(f"获取问候语失败: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': '获取问候语失败'
        }), 500


@dashboard_bp.route('/api/templates/quick')
def get_quick_templates():
    """
    获取快速模板API
    返回首页显示的快速模板列表
    
    返回:
        JSON格式的模板列表
    """
    try:
        logger.info("获取快速模板")
        
        # 从服务层获取模板数据
        templates = dashboard_service.get_quick_templates()
        
        return jsonify({
            'success': True,
            'data': {
                'templates': templates
            }
        })
        
    except Exception as e:
        logger.error(f"获取快速模板失败: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': '获取模板失败'
        }), 500


@dashboard_bp.route('/api/prompts/recent')
def get_recent_prompts():
    """
    获取最近使用的Prompts API
    
    查询参数:
        limit: 返回数量限制（默认4）
        include_shared: 是否包含共享的Prompts（默认True）
    
    返回:
        JSON格式的Prompt列表
    """
    try:
        # 获取查询参数
        limit = request.args.get('limit', 4, type=int)
        include_shared = request.args.get('include_shared', 'true').lower() == 'true'
        
        logger.info(f"获取最近使用的Prompts, limit={limit}, include_shared={include_shared}")
        
        # 从服务层获取数据
        prompts = dashboard_service.get_recent_prompts(
            limit=limit,
            include_shared=include_shared
        )
        
        return jsonify({
            'success': True,
            'data': {
                'prompts': prompts,
                'totalCount': len(prompts)
            }
        })
        
    except Exception as e:
        logger.error(f"获取最近Prompts失败: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': '获取数据失败'
        }), 500


@dashboard_bp.route('/api/activities/feed')
def get_activity_feed():
    """
    获取协作动态API
    
    查询参数:
        limit: 返回数量限制（默认20）
        offset: 偏移量（默认0）
    
    返回:
        JSON格式的动态列表
    """
    try:
        # 获取查询参数
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        logger.info(f"获取协作动态, limit={limit}, offset={offset}")
        
        # 从服务层获取数据
        activities = dashboard_service.get_activity_feed(
            limit=limit,
            offset=offset
        )
        
        return jsonify({
            'success': True,
            'data': {
                'activities': activities,
                'hasMore': len(activities) == limit
            }
        })
        
    except Exception as e:
        logger.error(f"获取协作动态失败: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': '获取动态失败'
        }), 500


@dashboard_bp.route('/api/integrations/status')
def get_api_status():
    """
    获取API连接状态
    检查各AI平台的连接状态
    
    返回:
        JSON格式的API状态信息
    """
    try:
        logger.info("检查API连接状态")
        
        # 从服务层获取状态数据
        status_data = dashboard_service.check_api_status()
        
        return jsonify({
            'success': True,
            'data': status_data
        })
        
    except Exception as e:
        logger.error(f"检查API状态失败: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': '检查状态失败'
        }), 500


@dashboard_bp.route('/api/integrations/<api_id>/test', methods=['POST'])
def test_api_connection(api_id):
    """
    测试API连接
    
    参数:
        api_id: API标识符
    
    请求体:
        test_prompt: 测试提示词（可选）
    
    返回:
        JSON格式的测试结果
    """
    try:
        logger.info(f"测试API连接: {api_id}")
        
        # 获取请求数据
        data = request.get_json() or {}
        test_prompt = data.get('test_prompt', 'Hello, this is a test.')
        
        # 调用服务层进行测试
        result = dashboard_service.test_api_connection(api_id, test_prompt)
        
        return jsonify({
            'success': result['success'],
            'data': result
        })
        
    except Exception as e:
        logger.error(f"测试API连接失败: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': '测试失败'
        }), 500