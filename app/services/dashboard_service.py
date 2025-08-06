"""
首页服务层
作者: Claude
创建时间: 2025-08-06
功能: 处理首页相关的业务逻辑和数据聚合
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

from app.common.logger import get_logger

# 获取日志器
logger = get_logger(__name__)


class DashboardService:
    """
    首页服务类
    负责处理首页相关的所有业务逻辑
    """
    
    def __init__(self):
        """
        初始化首页服务
        """
        self.logger = logger
        
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        获取首页所有数据
        聚合多个数据源，返回首页需要的完整数据
        
        返回:
            包含首页所有数据的字典
        """
        try:
            # 聚合各项数据
            data = {
                'greeting': self.get_user_greeting_data(),
                'quickTemplates': self.get_quick_templates(),
                'recentPrompts': self.get_recent_prompts(limit=4),
                'activities': self.get_activity_feed(limit=10),
                'apiStatus': self.check_api_status()
            }
            
            return data
            
        except Exception as e:
            self.logger.error(f"获取首页数据失败: {str(e)}", exc_info=True)
            raise
    
    def get_user_greeting_data(self) -> Dict[str, Any]:
        """
        获取用户问候数据
        包含用户名、今日任务数等信息
        
        返回:
            用户问候相关数据
        """
        try:
            # TODO: 从数据库获取实际用户数据
            # 现在返回模拟数据
            return {
                'userName': '用户',
                'todayTaskCount': 5,
                'pendingPrompts': 3,
                'completedToday': 2
            }
            
        except Exception as e:
            self.logger.error(f"获取用户问候数据失败: {str(e)}", exc_info=True)
            return {
                'userName': '用户',
                'todayTaskCount': 0,
                'pendingPrompts': 0,
                'completedToday': 0
            }
    
    def get_quick_templates(self) -> List[Dict[str, Any]]:
        """
        获取快速模板列表
        
        返回:
            模板列表
        """
        try:
            # TODO: 从数据库获取模板数据
            # 现在返回模拟数据
            templates = [
                {
                    'id': 'tpl_001',
                    'icon': 'message-circle',
                    'title': '对话助手',
                    'description': '智能客服和聊天机器人',
                    'category': 'conversation',
                    'promptTemplate': '你是一个专业的客服助手...',
                    'variables': ['user_question'],
                    'usageCount': 156
                },
                {
                    'id': 'tpl_002',
                    'icon': 'file-text',
                    'title': '内容创作',
                    'description': '文章、博客和营销文案',
                    'category': 'content',
                    'promptTemplate': '请为{{topic}}撰写一篇文章...',
                    'variables': ['topic', 'word_count'],
                    'usageCount': 234
                },
                {
                    'id': 'tpl_003',
                    'icon': 'code',
                    'title': '代码助手',
                    'description': '代码生成和文档编写',
                    'category': 'code',
                    'promptTemplate': '请帮我编写以下功能的代码...',
                    'variables': ['language', 'task_description'],
                    'usageCount': 189
                },
                {
                    'id': 'tpl_004',
                    'icon': 'shopping-cart',
                    'title': '电商运营',
                    'description': '商品描述和营销素材',
                    'category': 'ecommerce',
                    'promptTemplate': '为{{product_name}}撰写商品详情...',
                    'variables': ['product_name', 'features'],
                    'usageCount': 142
                }
            ]
            
            return templates
            
        except Exception as e:
            self.logger.error(f"获取快速模板失败: {str(e)}", exc_info=True)
            return []
    
    def get_recent_prompts(self, limit: int = 4, include_shared: bool = True) -> List[Dict[str, Any]]:
        """
        获取最近使用的Prompts
        
        参数:
            limit: 返回数量限制
            include_shared: 是否包含共享的Prompts
            
        返回:
            Prompt列表
        """
        try:
            # TODO: 从数据库获取实际数据
            # 现在返回模拟数据
            prompts = [
                {
                    'id': 'prompt_001',
                    'title': '产品文案生成器',
                    'content': '请为我的{{产品名称}}生成一段吸引人的营销文案...',
                    'preview': '请为我的{{产品名称}}生成一段吸引人的营销文案。重点突出{{核心卖点}}，文案风格：1. 简洁有力 2. 控制在100字以内...',
                    'category': '营销文案',
                    'categoryColor': 'orange',
                    'version': 'v1.3',
                    'lastUsed': '2小时前',
                    'score': 4.8,
                    'creator': '我',
                    'isShared': False
                },
                {
                    'id': 'prompt_002',
                    'title': 'API文档生成',
                    'content': '根据下面数据库表结构生成详细的API文档...',
                    'preview': '根据下面数据库表结构详细的API文档：{{函数签名}} 请包含：1. 函数描述和用途 2. 参数说明（类型、是否必需、默认值）...',
                    'category': '代码注释',
                    'categoryColor': 'blue',
                    'version': 'v2.1',
                    'lastUsed': '1天前',
                    'score': 4.5,
                    'creator': '我',
                    'isShared': True
                },
                {
                    'id': 'prompt_003',
                    'title': '客服回复模板',
                    'content': '作为专业的客服人员，请根据客户问题提供回复...',
                    'preview': '作为专业的客服人员，请根据客户问题：{{问题内容}}，提供礼貌、专业的回复。要求：1. 态度友好 2. 解决方案清晰...',
                    'category': '客服对话',
                    'categoryColor': 'green',
                    'version': 'v1.8',
                    'lastUsed': '3天前',
                    'score': 4.9,
                    'creator': '团队',
                    'isShared': True
                },
                {
                    'id': 'prompt_004',
                    'title': 'SEO文章优化',
                    'content': '优化以下文章以提高SEO排名...',
                    'preview': '优化以下文章以提高SEO排名：{{文章内容}}。请关注：1. 关键词密度 2. 标题优化 3. 元描述生成...',
                    'category': '内容创作',
                    'categoryColor': 'purple',
                    'version': 'v2.0',
                    'lastUsed': '1周前',
                    'score': 4.7,
                    'creator': '我',
                    'isShared': False
                }
            ]
            
            # 根据参数过滤
            if not include_shared:
                prompts = [p for p in prompts if not p['isShared']]
            
            # 限制返回数量
            return prompts[:limit]
            
        except Exception as e:
            self.logger.error(f"获取最近Prompts失败: {str(e)}", exc_info=True)
            return []
    
    def get_activity_feed(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        获取协作动态
        
        参数:
            limit: 返回数量限制
            offset: 偏移量
            
        返回:
            动态列表
        """
        try:
            # TODO: 从数据库获取实际数据
            # 现在返回模拟数据
            activities = [
                {
                    'id': 'act_001',
                    'userId': 'user_001',
                    'userName': '你',
                    'userAvatar': None,
                    'action': 'tested',
                    'actionText': '测试了',
                    'targetType': 'prompt',
                    'targetId': 'prompt_001',
                    'targetName': '产品文案生成器 v1.3',
                    'timestamp': '2小时前',
                    'metadata': {
                        'score': 4.8,
                        'testCount': 5
                    }
                },
                {
                    'id': 'act_002',
                    'userId': 'user_002',
                    'userName': '李小明',
                    'userAvatar': None,
                    'action': 'shared',
                    'actionText': '分享了',
                    'targetType': 'prompt',
                    'targetId': 'prompt_005',
                    'targetName': 'GPT-4提示词优化技巧',
                    'timestamp': '4小时前',
                    'metadata': {
                        'collaborators': ['张三', '王五']
                    }
                },
                {
                    'id': 'act_003',
                    'userId': 'user_001',
                    'userName': '你',
                    'userAvatar': None,
                    'action': 'created',
                    'actionText': '创建了',
                    'targetType': 'prompt',
                    'targetId': 'prompt_002',
                    'targetName': 'API文档生成器',
                    'timestamp': '昨天',
                    'metadata': {}
                },
                {
                    'id': 'act_004',
                    'userId': 'user_002',
                    'userName': '李小明',
                    'userAvatar': None,
                    'action': 'updated',
                    'actionText': '优化了',
                    'targetType': 'prompt',
                    'targetId': 'prompt_003',
                    'targetName': '客服回复模板',
                    'timestamp': '2天前',
                    'metadata': {
                        'version': 'v1.8'
                    }
                }
            ]
            
            # 应用分页
            start = offset
            end = offset + limit
            return activities[start:end]
            
        except Exception as e:
            self.logger.error(f"获取协作动态失败: {str(e)}", exc_info=True)
            return []
    
    def check_api_status(self) -> Dict[str, Any]:
        """
        检查API连接状态
        
        返回:
            API状态信息
        """
        try:
            # TODO: 实际检查API连接
            # 现在返回模拟数据
            api_status = {
                'apis': [
                    {
                        'id': 'openai',
                        'name': 'OpenAI GPT-4',
                        'provider': 'openai',
                        'status': 'connected',
                        'lastChecked': datetime.now().isoformat(),
                        'responseTime': 120,
                        'configuration': {
                            'hasApiKey': True,
                            'model': 'gpt-4',
                            'endpoint': 'https://api.openai.com/v1'
                        }
                    },
                    {
                        'id': 'claude',
                        'name': 'Claude 3',
                        'provider': 'anthropic',
                        'status': 'connected',
                        'lastChecked': datetime.now().isoformat(),
                        'responseTime': 95,
                        'configuration': {
                            'hasApiKey': True,
                            'model': 'claude-3-opus',
                            'endpoint': 'https://api.anthropic.com'
                        }
                    },
                    {
                        'id': 'wenxin',
                        'name': '文心一言',
                        'provider': 'baidu',
                        'status': 'disconnected',
                        'lastChecked': datetime.now().isoformat(),
                        'errorMessage': 'API密钥未配置',
                        'configuration': {
                            'hasApiKey': False,
                            'model': 'ERNIE-Bot-4',
                            'endpoint': None
                        }
                    }
                ],
                'lastHealthCheck': datetime.now().isoformat(),
                'overallStatus': 'partial'  # healthy, partial, critical
            }
            
            return api_status
            
        except Exception as e:
            self.logger.error(f"检查API状态失败: {str(e)}", exc_info=True)
            return {
                'apis': [],
                'lastHealthCheck': datetime.now().isoformat(),
                'overallStatus': 'critical'
            }
    
    def test_api_connection(self, api_id: str, test_prompt: str = "Hello") -> Dict[str, Any]:
        """
        测试API连接
        
        参数:
            api_id: API标识符
            test_prompt: 测试提示词
            
        返回:
            测试结果
        """
        try:
            # TODO: 实际调用API进行测试
            # 现在返回模拟数据
            
            # 模拟不同API的测试结果
            if api_id == 'openai':
                return {
                    'success': True,
                    'responseTime': 150,
                    'sampleResponse': 'Hello! How can I assist you today?'
                }
            elif api_id == 'claude':
                return {
                    'success': True,
                    'responseTime': 120,
                    'sampleResponse': 'Hello! I\'m Claude, an AI assistant.'
                }
            elif api_id == 'wenxin':
                return {
                    'success': False,
                    'errorMessage': 'API密钥未配置，请先配置API密钥'
                }
            else:
                return {
                    'success': False,
                    'errorMessage': f'未知的API: {api_id}'
                }
                
        except Exception as e:
            self.logger.error(f"测试API连接失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'errorMessage': str(e)
            }