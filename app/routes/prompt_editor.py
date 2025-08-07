"""
Prompt编辑器路由模块
处理Prompt编辑页面相关的所有HTTP请求
"""
from flask import Blueprint, render_template, request, jsonify, session
from app.common.logger import get_logger
from app.services.prompt_service import PromptService
from functools import wraps

logger = get_logger(__name__)

# 创建蓝图
prompt_editor_bp = Blueprint('prompt_editor', __name__, url_prefix='/prompt')


def login_required(f):
    """
    登录验证装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # TODO: 实现真实的登录验证
        # 临时使用模拟用户ID
        if 'user_id' not in session:
            session['user_id'] = 1  # 模拟用户ID
        return f(*args, **kwargs)
    return decorated_function


# ============== 页面路由 ==============

@prompt_editor_bp.route('/editor', methods=['GET'])
@prompt_editor_bp.route('/editor/<int:prompt_id>', methods=['GET'])
@login_required
def editor_page(prompt_id=None):
    """
    Prompt编辑器页面
    
    Args:
        prompt_id: Prompt ID（编辑现有Prompt时提供）
    """
    user_id = session.get('user_id')
    
    # 如果是编辑现有Prompt，获取数据
    prompt_data = None
    if prompt_id:
        prompt_data = PromptService.get_prompt(prompt_id, user_id)
        if not prompt_data:
            return render_template('404.html'), 404
    
    return render_template('prompt_editor.html', 
                         prompt=prompt_data,
                         is_new=prompt_id is None)


# ============== API路由 ==============

@prompt_editor_bp.route('/api/create', methods=['POST'])
@login_required
def create_prompt():
    """
    创建新的Prompt
    """
    try:
        user_id = session.get('user_id')
        data = request.json
        
        # 验证必填字段
        if not data.get('title'):
            return jsonify({'success': False, 'error': '标题不能为空'}), 400
        
        # 创建Prompt
        result = PromptService.create_prompt(
            user_id=user_id,
            title=data['title'],
            content=data.get('content', ''),
            category=data.get('category', 'general'),
            description=data.get('description', ''),
            tags=data.get('tags', []),
            visibility=data.get('visibility', 'private'),
            language=data.get('language', 'zh-CN'),
            difficulty=data.get('difficulty', 'intermediate')
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"创建Prompt失败: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': '服务器错误'}), 500


@prompt_editor_bp.route('/api/<int:prompt_id>/update', methods=['PUT'])
@login_required
def update_prompt(prompt_id):
    """
    更新Prompt
    
    Args:
        prompt_id: Prompt ID
    """
    try:
        user_id = session.get('user_id')
        data = request.json
        
        # 更新Prompt
        result = PromptService.update_prompt(
            prompt_id=prompt_id,
            user_id=user_id,
            **data
        )
        
        if not result['success']:
            return jsonify(result), 400
            
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"更新Prompt失败: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': '服务器错误'}), 500


@prompt_editor_bp.route('/api/<int:prompt_id>', methods=['GET'])
@login_required
def get_prompt(prompt_id):
    """
    获取Prompt详情
    
    Args:
        prompt_id: Prompt ID
    """
    try:
        user_id = session.get('user_id')
        prompt_data = PromptService.get_prompt(prompt_id, user_id)
        
        if not prompt_data:
            return jsonify({'success': False, 'error': 'Prompt不存在或无权限'}), 404
        
        return jsonify({
            'success': True,
            'data': prompt_data
        })
        
    except Exception as e:
        logger.error(f"获取Prompt失败: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': '服务器错误'}), 500


@prompt_editor_bp.route('/api/<int:prompt_id>/versions', methods=['GET'])
@login_required
def get_versions(prompt_id):
    """
    获取Prompt版本历史
    
    Args:
        prompt_id: Prompt ID
    """
    try:
        user_id = session.get('user_id')
        versions = PromptService.get_version_history(prompt_id, user_id)
        
        return jsonify({
            'success': True,
            'versions': versions
        })
        
    except Exception as e:
        logger.error(f"获取版本历史失败: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': '服务器错误'}), 500


@prompt_editor_bp.route('/api/<int:prompt_id>/analyze', methods=['POST'])
@login_required
def analyze_prompt(prompt_id):
    """
    分析Prompt内容
    提取变量、计算Token数等
    
    Args:
        prompt_id: Prompt ID
    """
    try:
        data = request.json
        content = data.get('content', '')
        
        # 分析内容
        analysis = PromptService.analyze_content(content)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        logger.error(f"分析Prompt失败: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': '服务器错误'}), 500


# ============== 自动保存API ==============
# 注: 自动保存功能已改为使用localStorage在前端实现


# ============== 测试API ==============

@prompt_editor_bp.route('/api/<int:prompt_id>/test', methods=['POST'])
@login_required
def test_prompt(prompt_id):
    """
    测试Prompt (实时测试，不保存历史)
    
    Args:
        prompt_id: Prompt ID
    """
    try:
        user_id = session.get('user_id')
        data = request.json
        
        # TODO: 实现实时API调用测试
        # 这里将直接调用OpenAI或Claude API进行测试
        # 不保存测试结果到数据库
        
        return jsonify({
            'success': True,
            'message': '测试功能待实现',
            'result': '实时测试结果将在此处返回'
        })
        
    except Exception as e:
        logger.error(f"测试Prompt失败: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': '测试失败'}), 500


# 测试历史功能已移除，测试改为实时执行不保存历史


# ============== 标签和分类API ==============



@prompt_editor_bp.route('/api/categories', methods=['GET'])
def get_categories():
    """
    获取分类列表
    """
    categories = [
        {'value': 'marketing', 'label': '营销文案', 'color': 'bg-chart-1'},
        {'value': 'customer-service', 'label': '客服对话', 'color': 'bg-chart-2'},
        {'value': 'product', 'label': '产品描述', 'color': 'bg-chart-3'},
        {'value': 'code', 'label': '代码注释', 'color': 'bg-chart-4'},
        {'value': 'creative', 'label': '创意写作', 'color': 'bg-chart-5'},
        {'value': 'analysis', 'label': '数据分析', 'color': 'bg-green-500'}
    ]
    
    return jsonify({
        'success': True,
        'categories': categories
    })



# ============== API提供商配置 ==============

@prompt_editor_bp.route('/api/providers', methods=['GET'])
def get_api_providers():
    """
    获取可用的API提供商列表（从配置中读取）
    """
    # 从配置中返回固定的提供商
    providers = [
        {
            'code': 'openai',
            'name': 'OpenAI',
            'model': 'Latest',  # 总是使用最新模型
            'enabled': True
        },
        {
            'code': 'claude',
            'name': 'Claude',
            'model': 'Latest',  # 总是使用最新模型
            'enabled': True
        }
    ]
    
    return jsonify({
        'success': True,
        'providers': providers
    })