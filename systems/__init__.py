"""
命理系统实现模块
"""

from typing import Dict, Type
from core.base_system import BaseFortuneSystem

# 系统注册表
_SYSTEMS: Dict[str, Type[BaseFortuneSystem]] = {}


def register_system(name: str, system_class: Type[BaseFortuneSystem]):
    """
    注册命理系统
    
    Args:
        name: 系统名称（用于标识）
        system_class: 系统类
    """
    _SYSTEMS[name] = system_class


def get_system(name: str) -> BaseFortuneSystem:
    """
    获取命理系统实例
    
    Args:
        name: 系统名称
        
    Returns:
        系统实例
        
    Raises:
        ValueError: 系统未注册
    """
    if name not in _SYSTEMS:
        raise ValueError(f"System '{name}' not registered. Available: {list(_SYSTEMS.keys())}")
    
    return _SYSTEMS[name]()


def list_systems() -> list:
    """
    列出所有已注册的系统
    
    Returns:
        系统名称列表
    """
    return list(_SYSTEMS.keys())


# 自动导入并注册所有系统
try:
    from .ziwei import ZiweiSystem
    register_system('ziwei', ZiweiSystem)
except ImportError:
    pass

try:
    from .bazi import BaziSystem
    register_system('bazi', BaziSystem)
except ImportError:
    pass

try:
    from .astrology import AstrologySystem
    register_system('astrology', AstrologySystem)
except ImportError:
    pass


__all__ = ['register_system', 'get_system', 'list_systems']
