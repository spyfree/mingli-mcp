"""
紫微斗数系统实现

基于py-iztro库实现紫微斗数排盘和分析
"""

import logging
from typing import Dict, Any, Optional, TYPE_CHECKING
from datetime import datetime
from core.base_system import BaseFortuneSystem
from .formatter import ZiweiFormatter

logger = logging.getLogger(__name__)

# 使用 TYPE_CHECKING 避免运行时导入错误
if TYPE_CHECKING:
    from py_iztro import Astro

try:
    from py_iztro import Astro
    astro = Astro()
    PYIZTRO_AVAILABLE = True
except ImportError:
    logger.warning("py-iztro not installed, ZiweiSystem will not work")
    PYIZTRO_AVAILABLE = False
    astro = None  # type: ignore
    Astro = None  # type: ignore


class ZiweiSystem(BaseFortuneSystem):
    """紫微斗数系统实现"""
    
    # 十二宫位名称
    PALACES = [
        '命宫', '兄弟', '夫妻', '子女', '财帛', '疾厄',
        '迁移', '仆役', '官禄', '田宅', '福德', '父母'
    ]
    
    def __init__(self):
        if not PYIZTRO_AVAILABLE:
            raise RuntimeError("py-iztro library is not installed. Please install it with: pip install py-iztro")
        self.formatter = ZiweiFormatter()
    
    def get_system_name(self) -> str:
        return "紫微斗数"
    
    def get_system_version(self) -> str:
        try:
            import pyiztro
            return getattr(pyiztro, '__version__', '1.0.0')
        except:
            return '1.0.0'
    
    def get_chart(self, birth_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取紫微斗数排盘
        
        Args:
            birth_info: 生辰信息
            
        Returns:
            排盘详细信息
        """
        self.validate_birth_info(birth_info)
        
        try:
            # 根据历法类型调用不同的方法
            if birth_info.get('calendar', 'solar') == 'lunar':
                astrolabe = astro.by_lunar(
                    birth_info['date'],
                    birth_info['time_index'],
                    birth_info['gender'],
                    birth_info.get('is_leap_month', False)
                )
            else:
                astrolabe = astro.by_solar(
                    birth_info['date'],
                    birth_info['time_index'],
                    birth_info['gender']
                )
            
            # 格式化输出
            return self.formatter.format_chart(astrolabe)
            
        except Exception as e:
            logger.exception("Error generating ziwei chart")
            raise RuntimeError(f"排盘失败: {str(e)}")
    
    def get_fortune(
        self, 
        birth_info: Dict[str, Any], 
        query_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        获取紫微斗数运势（大限、流年、流月、流日、流时）
        
        Args:
            birth_info: 生辰信息
            query_date: 查询日期，默认当前时间
            
        Returns:
            运势信息
        """
        self.validate_birth_info(birth_info)
        
        if query_date is None:
            query_date = datetime.now()
        
        try:
            # 先获取星盘
            if birth_info.get('calendar', 'solar') == 'lunar':
                astrolabe = astro.by_lunar(
                    birth_info['date'],
                    birth_info['time_index'],
                    birth_info['gender'],
                    birth_info.get('is_leap_month', False)
                )
            else:
                astrolabe = astro.by_solar(
                    birth_info['date'],
                    birth_info['time_index'],
                    birth_info['gender']
                )
            
            # 获取运势
            horoscope = astrolabe.horoscope(query_date)
            
            # 格式化输出
            return self.formatter.format_fortune(horoscope, query_date)
            
        except Exception as e:
            logger.exception("Error generating ziwei fortune")
            raise RuntimeError(f"运势查询失败: {str(e)}")
    
    def analyze_palace(
        self, 
        birth_info: Dict[str, Any], 
        palace_name: str
    ) -> Dict[str, Any]:
        """
        分析特定宫位
        
        Args:
            birth_info: 生辰信息
            palace_name: 宫位名称
            
        Returns:
            宫位详细分析
        """
        if palace_name not in self.PALACES:
            raise ValueError(f"无效的宫位名称: {palace_name}. 有效宫位: {', '.join(self.PALACES)}")
        
        self.validate_birth_info(birth_info)
        
        try:
            # 获取完整星盘
            chart = self.get_chart(birth_info)
            
            # 找到指定宫位
            target_palace = None
            for palace in chart['palaces']:
                if palace['name'] == palace_name:
                    target_palace = palace
                    break
            
            if target_palace is None:
                raise ValueError(f"未找到宫位: {palace_name}")
            
            # 格式化宫位分析
            return self.formatter.format_palace_analysis(target_palace, chart['basic_info'])
            
        except Exception as e:
            logger.exception("Error analyzing palace")
            raise RuntimeError(f"宫位分析失败: {str(e)}")
    
    def get_supported_palaces(self) -> list:
        """返回支持的宫位列表"""
        return self.PALACES.copy()
    
    def get_capabilities(self) -> Dict[str, bool]:
        """返回系统功能支持"""
        return {
            'chart': True,
            'fortune': True,
            'palace_analysis': True,
            'compatibility': False,  # 暂不支持合盘
            'transit': False,  # 暂不支持推运
        }
