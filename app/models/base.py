"""
数据模型基类
提供通用的数据库操作方法
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
import json


class BaseModel:
    """
    数据模型基类
    提供基础的CRUD操作和JSON序列化功能
    """
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将模型对象转换为字典
        
        Returns:
            dict: 模型数据字典
        """
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                if isinstance(value, datetime):
                    result[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(value, bytes):
                    result[key] = value.decode('utf-8')
                elif hasattr(value, 'to_dict'):
                    result[key] = value.to_dict()
                else:
                    result[key] = value
        return result
    
    def to_json(self) -> str:
        """
        将模型对象转换为JSON字符串
        
        Returns:
            str: JSON字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """
        从字典创建模型对象
        
        Args:
            data: 数据字典
            
        Returns:
            模型对象实例
        """
        instance = cls()
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        return instance
    
    def parse_json_field(self, field_name: str, default: Any = None) -> Any:
        """
        解析JSON字段
        
        Args:
            field_name: 字段名
            default: 默认值
            
        Returns:
            解析后的Python对象
        """
        field_value = getattr(self, field_name, None)
        if field_value:
            try:
                if isinstance(field_value, str):
                    return json.loads(field_value)
                return field_value
            except (json.JSONDecodeError, TypeError):
                return default
        return default
    
    def set_json_field(self, field_name: str, value: Any) -> None:
        """
        设置JSON字段的值
        
        Args:
            field_name: 字段名
            value: 要设置的值（Python对象）
        """
        if value is not None:
            if not isinstance(value, str):
                value = json.dumps(value, ensure_ascii=False)
            setattr(self, field_name, value)
        else:
            setattr(self, field_name, None)