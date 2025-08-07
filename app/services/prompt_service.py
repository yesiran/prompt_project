"""
Prompt核心业务服务
处理Prompt的创建、编辑、版本管理等核心功能
"""
import uuid
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from app.common.logger import get_logger
from app.models import Prompt, PromptVersion, PromptTag
from app.common.database import get_db_connection

logger = get_logger(__name__)


class PromptService:
    """
    Prompt业务服务类
    提供Prompt相关的核心业务逻辑
    """
    
    @staticmethod
    def create_prompt(user_id: int, workspace_id: int, title: str, content: str = '', 
                     category: str = 'general', **kwargs) -> Dict[str, Any]:
        """
        创建新的Prompt
        
        Args:
            user_id: 用户ID
            workspace_id: 工作空间ID
            title: Prompt标题
            content: Prompt内容
            category: 分类
            **kwargs: 其他可选参数
            
        Returns:
            dict: 创建的Prompt信息
        """
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 生成UUID
                    prompt_uuid = str(uuid.uuid4())
                    
                    # 插入Prompt基础信息
                    sql = """
                        INSERT INTO prompts (uuid, title, description, category, user_id, 
                                           workspace_id, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (
                        prompt_uuid,
                        title,
                        kwargs.get('description', ''),
                        category,
                        user_id,
                        workspace_id,
                        1  # 正常状态
                    ))
                    prompt_id = cursor.lastrowid
                    
                    # 创建初始版本
                    version_data = PromptService._create_version(
                        cursor, prompt_id, 'v1.0', content, user_id, is_current=True
                    )
                    
                    
                    # 保存标签
                    tags = kwargs.get('tags', [])
                    if tags:
                        PromptService._save_tags(cursor, prompt_id, tags)
                    
                    
                    conn.commit()
                    
                    logger.info(f"创建Prompt成功: ID={prompt_id}, UUID={prompt_uuid}")
                    
                    return {
                        'success': True,
                        'prompt_id': prompt_id,
                        'uuid': prompt_uuid,
                        'version_id': version_data['id'],
                        'version': version_data['version']
                    }
                    
        except Exception as e:
            logger.error(f"创建Prompt失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f'创建失败: {str(e)}'
            }
    
    @staticmethod
    def update_prompt(prompt_id: int, user_id: int, **updates) -> Dict[str, Any]:
        """
        更新Prompt信息
        
        Args:
            prompt_id: Prompt ID
            user_id: 用户ID
            **updates: 要更新的字段
            
        Returns:
            dict: 更新结果
        """
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 检查权限
                    sql = "SELECT user_id, status FROM prompts WHERE id = %s"
                    cursor.execute(sql, (prompt_id,))
                    prompt = cursor.fetchone()
                    
                    if not prompt:
                        return {'success': False, 'error': 'Prompt不存在'}
                    
                    if prompt['user_id'] != user_id:
                        return {'success': False, 'error': '无权限编辑此Prompt'}
                    
                    # 更新基础信息
                    allowed_fields = ['title', 'description', 'category', 'status']
                    update_fields = []
                    update_values = []
                    
                    for field in allowed_fields:
                        if field in updates:
                            update_fields.append(f"{field} = %s")
                            update_values.append(updates[field])
                    
                    if update_fields:
                        sql = f"""
                            UPDATE prompts 
                            SET {', '.join(update_fields)}, update_time = NOW()
                            WHERE id = %s
                        """
                        update_values.append(prompt_id)
                        cursor.execute(sql, update_values)
                    
                    # 更新内容（创建新版本或更新当前版本）
                    if 'content' in updates:
                        content = updates['content']
                        create_new_version = updates.get('create_new_version', False)
                        
                        if create_new_version:
                            # 创建新版本
                            new_version = PromptService._get_next_version(cursor, prompt_id)
                            version_data = PromptService._create_version(
                                cursor, prompt_id, new_version, content, user_id, 
                                is_current=True, change_log=updates.get('change_log', '')
                            )
                        else:
                            # 更新当前版本
                            sql = """
                                UPDATE prompt_versions 
                                SET content = %s, update_time = NOW()
                                WHERE prompt_id = %s AND is_current = 1
                            """
                            cursor.execute(sql, (content, prompt_id))
                            
                            # 获取版本ID
                            sql = "SELECT id FROM prompt_versions WHERE prompt_id = %s AND is_current = 1"
                            cursor.execute(sql, (prompt_id,))
                            version = cursor.fetchone()
                            version_data = {'id': version['id']}
                    
                    # 更新标签
                    if 'tags' in updates:
                        PromptService._update_tags(cursor, prompt_id, updates['tags'])
                    
                    conn.commit()
                    
                    logger.info(f"更新Prompt成功: ID={prompt_id}")
                    return {'success': True, 'prompt_id': prompt_id}
                    
        except Exception as e:
            logger.error(f"更新Prompt失败: {str(e)}", exc_info=True)
            return {'success': False, 'error': f'更新失败: {str(e)}'}
    
    @staticmethod
    def get_prompt(prompt_id: int, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        获取Prompt详情
        
        Args:
            prompt_id: Prompt ID
            user_id: 用户ID（用于权限检查）
            
        Returns:
            dict: Prompt详情，如果不存在或无权限则返回None
        """
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 获取Prompt基础信息
                    sql = """
                        SELECT p.*
                        FROM prompts p
                        WHERE p.id = %s AND p.status != 0
                    """
                    cursor.execute(sql, (prompt_id,))
                    prompt = cursor.fetchone()
                    
                    if not prompt:
                        return None
                    
                    # 权限检查：检查用户是否属于同一工作空间
                    # TODO: 实现工作空间成员检查
                    # 暂时只检查是否是创建者
                    # if not PromptService._can_access_prompt(cursor, prompt, user_id):
                    #     return None
                    
                    # 获取当前版本
                    sql = """
                        SELECT * FROM prompt_versions 
                        WHERE prompt_id = %s AND is_current = 1
                    """
                    cursor.execute(sql, (prompt_id,))
                    version = cursor.fetchone()
                    
                    # 获取标签
                    sql = "SELECT tag_name FROM prompt_tags WHERE prompt_id = %s"
                    cursor.execute(sql, (prompt_id,))
                    tags = [row['tag_name'] for row in cursor.fetchall()]
                    
                    # 组装返回数据
                    result = dict(prompt)
                    result['current_version'] = dict(version) if version else None
                    result['tags'] = tags
                    
                    return result
                    
        except Exception as e:
            logger.error(f"获取Prompt失败: {str(e)}", exc_info=True)
            return None
    
    
    @staticmethod
    def _create_version(cursor, prompt_id: int, version: str, content: str, 
                       author_id: int, is_current: bool = False, 
                       change_log: str = '') -> Dict[str, Any]:
        """
        创建新版本
        
        Args:
            cursor: 数据库游标
            prompt_id: Prompt ID
            version: 版本号
            content: 内容
            author_id: 作者ID
            is_current: 是否为当前版本
            change_log: 变更日志
            
        Returns:
            dict: 版本信息
        """
        # 如果设为当前版本，先将其他版本设为非当前
        if is_current:
            sql = "UPDATE prompt_versions SET is_current = 0 WHERE prompt_id = %s"
            cursor.execute(sql, (prompt_id,))
        
        # 插入新版本
        sql = """
            INSERT INTO prompt_versions (prompt_id, version, content, 
                                       change_log, is_current, author_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            prompt_id, version, content, change_log, 
            1 if is_current else 0, author_id
        ))
        
        return {
            'id': cursor.lastrowid,
            'version': version
        }
    
    @staticmethod
    def _get_next_version(cursor, prompt_id: int) -> str:
        """
        获取下一个版本号
        
        Args:
            cursor: 数据库游标
            prompt_id: Prompt ID
            
        Returns:
            str: 下一个版本号
        """
        sql = """
            SELECT version FROM prompt_versions 
            WHERE prompt_id = %s 
            ORDER BY create_time DESC 
            LIMIT 1
        """
        cursor.execute(sql, (prompt_id,))
        result = cursor.fetchone()
        
        if result:
            current_version = result['version']
            # 解析版本号（v1.0 -> v1.1）
            match = re.match(r'v(\d+)\.(\d+)', current_version)
            if match:
                major = int(match.group(1))
                minor = int(match.group(2))
                return f'v{major}.{minor + 1}'
        
        return 'v1.0'
    
    
    @staticmethod
    def _save_tags(cursor, prompt_id: int, tags: List[str]) -> None:
        """
        保存标签
        
        Args:
            cursor: 数据库游标
            prompt_id: Prompt ID
            tags: 标签列表
        """
        for tag in tags:
            if tag:
                sql = """
                    INSERT IGNORE INTO prompt_tags (prompt_id, tag_name) 
                    VALUES (%s, %s)
                """
                cursor.execute(sql, (prompt_id, tag))
                
    
    @staticmethod
    def _update_tags(cursor, prompt_id: int, tags: List[str]) -> None:
        """
        更新标签
        
        Args:
            cursor: 数据库游标
            prompt_id: Prompt ID
            tags: 标签列表
        """
        # 删除旧标签
        sql = "DELETE FROM prompt_tags WHERE prompt_id = %s"
        cursor.execute(sql, (prompt_id,))
        
        # 保存新标签
        PromptService._save_tags(cursor, prompt_id, tags)