"""
工作空间数据模型
"""
from datetime import datetime
from typing import Optional, List
from .base import BaseModel


class Workspace(BaseModel):
    """
    工作空间模型
    """
    
    def __init__(self):
        self.id: Optional[int] = None
        self.name: Optional[str] = None
        self.description: Optional[str] = None
        self.type: str = 'personal'  # personal/shared
        self.owner_id: Optional[int] = None
        self.create_time: Optional[datetime] = None
        self.update_time: Optional[datetime] = None
        
        # 关联数据（非数据库字段）
        self.members: List['WorkspaceMember'] = []
        self.member_count: int = 0
    
    @property
    def type_text(self) -> str:
        """获取类型文本"""
        type_map = {
            'personal': '个人空间',
            'shared': '协作空间'
        }
        return type_map.get(self.type, '未知')
    
    def is_owner(self, user_id: int) -> bool:
        """
        检查用户是否是空间所有者
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 是否是所有者
        """
        return self.owner_id == user_id


class WorkspaceMember(BaseModel):
    """
    工作空间成员模型
    """
    
    def __init__(self):
        self.id: Optional[int] = None
        self.workspace_id: Optional[int] = None
        self.user_id: Optional[int] = None
        self.role: str = 'member'  # owner/member
        self.join_time: Optional[datetime] = None
        
        # 关联数据（非数据库字段）
        self.username: Optional[str] = None
        self.email: Optional[str] = None
    
    @property
    def role_text(self) -> str:
        """获取角色文本"""
        role_map = {
            'owner': '所有者',
            'member': '成员'
        }
        return role_map.get(self.role, '未知')
    
    def is_owner(self) -> bool:
        """是否是所有者"""
        return self.role == 'owner'