"""
Prompt核心数据模型
包含Prompt基础信息、版本、变量、标签等
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from .base import BaseModel


class Prompt(BaseModel):
    """
    Prompt基础信息模型
    """
    
    def __init__(self):
        self.id: Optional[int] = None
        self.uuid: Optional[str] = None
        self.title: Optional[str] = None
        self.description: Optional[str] = None
        self.category: str = 'general'
        self.user_id: Optional[int] = None
        self.workspace_id: Optional[int] = None
        self.status: int = 1  # 0:删除 1:正常
        self.create_time: Optional[datetime] = None
        self.update_time: Optional[datetime] = None
        
        # 关联数据（非数据库字段）
        self.current_version: Optional['PromptVersion'] = None
        self.tags: List[str] = []
        self.statistics: Optional['PromptStatistics'] = None
    
    @property
    def status_text(self) -> str:
        """获取状态文本"""
        status_map = {
            0: '已删除',
            1: '正常'
        }
        return status_map.get(self.status, '未知')
    
    def is_editable_by(self, user_id: int) -> bool:
        """
        检查用户是否可以编辑此Prompt
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 是否可编辑
        """
        return self.user_id == user_id and self.status == 1


class PromptVersion(BaseModel):
    """
    Prompt版本模型
    """
    
    def __init__(self):
        self.id: Optional[int] = None
        self.prompt_id: Optional[int] = None
        self.version: Optional[str] = None
        self.content: Optional[str] = None
        self.variables_json: Optional[str] = None
        self.change_log: Optional[str] = None
        self.is_current: int = 0
        self.published_at: Optional[datetime] = None
        self.author_id: Optional[int] = None
        self.create_time: Optional[datetime] = None
        self.update_time: Optional[datetime] = None
        
        # 关联数据（非数据库字段）
        self.variables: List['PromptVariable'] = []
    
    def get_variables(self) -> List[Dict[str, Any]]:
        """
        获取变量定义列表
        
        Returns:
            list: 变量定义列表
        """
        return self.parse_json_field('variables_json', [])
    
    def set_variables(self, variables: List[Dict[str, Any]]) -> None:
        """
        设置变量定义
        
        Args:
            variables: 变量定义列表
        """
        self.set_json_field('variables_json', variables)
    

    
    def get_ui_config(self) -> Dict[str, Any]:
        """
        获取UI配置
        
        Returns:
            dict: UI配置字典
        """
        return self.parse_json_field('ui_config', {})
    
    def set_ui_config(self, config: Dict[str, Any]) -> None:
        """
        设置UI配置
        
        Args:
            config: UI配置字典
        """
        self.set_json_field('ui_config', config)
    
    def validate_value(self, value: Any) -> tuple[bool, Optional[str]]:
        """
        验证变量值
        
        Args:
            value: 要验证的值
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        # 必填验证
        if self.required and not value:
            return False, f'{self.display_name or self.name}为必填项'
        
        # 类型验证
        rules = self.get_validation_rules()
        
        if self.type == 'number':
            try:
                num_value = float(value) if value else 0
                if 'min' in rules and num_value < rules['min']:
                    return False, f'值必须大于等于{rules["min"]}'
                if 'max' in rules and num_value > rules['max']:
                    return False, f'值必须小于等于{rules["max"]}'
            except (TypeError, ValueError):
                return False, '请输入有效的数字'
        
        elif self.type in ['text', 'multiline']:
            if value:
                str_value = str(value)
                if 'minLength' in rules and len(str_value) < rules['minLength']:
                    return False, f'长度至少为{rules["minLength"]}个字符'
                if 'maxLength' in rules and len(str_value) > rules['maxLength']:
                    return False, f'长度不能超过{rules["maxLength"]}个字符'
                if 'pattern' in rules:
                    import re
                    if not re.match(rules['pattern'], str_value):
                        return False, '格式不正确'
        
        elif self.type == 'select':
            if value and 'options' in rules:
                valid_options = [opt.get('value') for opt in rules['options']]
                if value not in valid_options:
                    return False, '请选择有效的选项'
        
        return True, None


class PromptTag(BaseModel):
    """
    Prompt标签模型
    """
    
    def __init__(self):
        self.id: Optional[int] = None
        self.prompt_id: Optional[int] = None
        self.tag_name: Optional[str] = None
        self.create_time: Optional[datetime] = None