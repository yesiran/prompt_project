"""
工作空间业务服务
处理工作空间的创建、管理和成员管理
"""
from typing import List, Dict, Any, Optional
from app.common.logger import get_logger
from app.models import Workspace, WorkspaceMember
from app.common.database import get_db_connection, Database

logger = get_logger(__name__)


class WorkspaceService:
    """
    工作空间服务类
    """
    
    @staticmethod
    def create_personal_workspace(user_id: int, username: str) -> int:
        """
        为用户创建个人工作空间
        
        Args:
            user_id: 用户ID
            username: 用户名
            
        Returns:
            int: 工作空间ID
        """
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 创建个人工作空间
                    sql = """
                        INSERT INTO workspaces (name, description, type, owner_id)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(sql, (
                        f"{username}的个人空间",
                        "个人工作空间",
                        'personal',
                        user_id
                    ))
                    workspace_id = cursor.lastrowid
                    
                    # 添加用户为所有者
                    sql = """
                        INSERT INTO workspace_members (workspace_id, user_id, role)
                        VALUES (%s, %s, %s)
                    """
                    cursor.execute(sql, (workspace_id, user_id, 'owner'))
                    
                    conn.commit()
                    
                    logger.info(f"创建个人工作空间成功: user_id={user_id}, workspace_id={workspace_id}")
                    return workspace_id
                    
        except Exception as e:
            logger.error(f"创建个人工作空间失败: {str(e)}", exc_info=True)
            return None
    
    @staticmethod
    def create_shared_workspace(owner_id: int, name: str, 
                               description: str = '') -> Dict[str, Any]:
        """
        创建协作空间
        
        Args:
            owner_id: 创建者ID
            name: 空间名称
            description: 空间描述
            
        Returns:
            dict: 创建结果
        """
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 创建协作空间
                    sql = """
                        INSERT INTO workspaces (name, description, type, owner_id)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(sql, (name, description, 'shared', owner_id))
                    workspace_id = cursor.lastrowid
                    
                    # 添加创建者为所有者
                    sql = """
                        INSERT INTO workspace_members (workspace_id, user_id, role)
                        VALUES (%s, %s, %s)
                    """
                    cursor.execute(sql, (workspace_id, owner_id, 'owner'))
                    
                    conn.commit()
                    
                    logger.info(f"创建协作空间成功: workspace_id={workspace_id}")
                    
                    return {
                        'success': True,
                        'workspace_id': workspace_id,
                        'message': '协作空间创建成功'
                    }
                    
        except Exception as e:
            logger.error(f"创建协作空间失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f'创建失败: {str(e)}'
            }
    
    @staticmethod
    def add_member(workspace_id: int, user_id: int, role: str = 'member') -> bool:
        """
        添加成员到工作空间
        
        Args:
            workspace_id: 工作空间ID
            user_id: 用户ID
            role: 角色（owner/member）
            
        Returns:
            bool: 是否成功
        """
        try:
            sql = """
                INSERT INTO workspace_members (workspace_id, user_id, role)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE role = VALUES(role)
            """
            Database.execute(sql, (workspace_id, user_id, role))
            
            logger.info(f"添加成员成功: workspace_id={workspace_id}, user_id={user_id}")
            return True
            
        except Exception as e:
            logger.error(f"添加成员失败: {str(e)}", exc_info=True)
            return False
    
    @staticmethod
    def remove_member(workspace_id: int, user_id: int) -> bool:
        """
        从工作空间移除成员
        
        Args:
            workspace_id: 工作空间ID
            user_id: 用户ID
            
        Returns:
            bool: 是否成功
        """
        try:
            sql = """
                DELETE FROM workspace_members 
                WHERE workspace_id = %s AND user_id = %s AND role != 'owner'
            """
            affected = Database.execute(sql, (workspace_id, user_id))
            
            if affected > 0:
                logger.info(f"移除成员成功: workspace_id={workspace_id}, user_id={user_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"移除成员失败: {str(e)}", exc_info=True)
            return False
    
    @staticmethod
    def get_user_workspaces(user_id: int) -> List[Dict[str, Any]]:
        """
        获取用户的所有工作空间
        
        Args:
            user_id: 用户ID
            
        Returns:
            list: 工作空间列表
        """
        sql = """
            SELECT w.*, wm.role
            FROM workspaces w
            INNER JOIN workspace_members wm ON w.id = wm.workspace_id
            WHERE wm.user_id = %s
            ORDER BY w.type DESC, w.create_time DESC
        """
        
        workspaces = Database.select_all(sql, (user_id,))
        return workspaces if workspaces else []
    
    @staticmethod
    def get_workspace_members(workspace_id: int) -> List[Dict[str, Any]]:
        """
        获取工作空间的所有成员
        
        Args:
            workspace_id: 工作空间ID
            
        Returns:
            list: 成员列表
        """
        sql = """
            SELECT wm.*, u.username, u.email
            FROM workspace_members wm
            LEFT JOIN users u ON wm.user_id = u.id
            WHERE wm.workspace_id = %s
            ORDER BY wm.role DESC, wm.join_time
        """
        
        members = Database.select_all(sql, (workspace_id,))
        return members if members else []
    
    @staticmethod
    def is_workspace_member(workspace_id: int, user_id: int) -> bool:
        """
        检查用户是否是工作空间成员
        
        Args:
            workspace_id: 工作空间ID
            user_id: 用户ID
            
        Returns:
            bool: 是否是成员
        """
        sql = """
            SELECT COUNT(*) as count
            FROM workspace_members
            WHERE workspace_id = %s AND user_id = %s
        """
        
        result = Database.select_one(sql, (workspace_id, user_id))
        return result and result['count'] > 0
    
    @staticmethod
    def get_workspace_prompts(workspace_id: int, user_id: int) -> List[Dict[str, Any]]:
        """
        获取工作空间的所有Prompt
        
        Args:
            workspace_id: 工作空间ID
            user_id: 用户ID（用于权限检查）
            
        Returns:
            list: Prompt列表
        """
        # 首先检查用户是否有权限访问
        if not WorkspaceService.is_workspace_member(workspace_id, user_id):
            return []
        
        sql = """
            SELECT p.*, u.username, pv.version, pv.content,
                   ps.use_count, ps.test_count, ps.favorite_count
            FROM prompts p
            LEFT JOIN users u ON p.user_id = u.id
            LEFT JOIN prompt_versions pv ON p.id = pv.prompt_id AND pv.is_current = 1
            LEFT JOIN prompt_statistics ps ON p.id = ps.prompt_id
            WHERE p.workspace_id = %s AND p.status = 1
            ORDER BY p.update_time DESC
        """
        
        prompts = Database.select_all(sql, (workspace_id,))
        return prompts if prompts else []