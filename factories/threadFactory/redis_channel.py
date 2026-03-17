import asyncio
import functools
from typing import Callable, Any, Dict, Optional

# 全局 asyncio 实例
asynio_instance = asyncio

class redisChannelListener:
    """Redis频道监听器包装器"""
    
    _wrapped_functions: Dict[str, Dict[str, Any]] = {}
    
    def __init__(self, default_values: Dict[str, Any]):
        """初始化包装器
        
        Args:
            default_values: 要替换的默认值字典
        """
        self.default_values = default_values
    
    def __call__(self, func: Callable) -> Callable:
        """包装函数
        
        Args:
            func: 要包装的函数
        
        Returns:
            包装后的函数
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 合并默认值和传入的参数
            combined_kwargs = self.default_values.copy()
            combined_kwargs.update(kwargs)
            return func(*args, **combined_kwargs)
        
        # 标记函数为被包装
        wrapper.__wrapped_by__ = 'redisChannelListener'
        wrapper.__default_values__ = self.default_values
        
        # 记录被包装的函数
        func_name = f"{func.__module__}.{func.__name__}"
        redisChannelListener._wrapped_functions[func_name] = {
            'function': func,
            'default_values': self.default_values
        }
        
        return wrapper
    
    @classmethod
    def get_wrapped_functions(cls) -> Dict[str, Dict[str, Any]]:
        """获取所有被包装的函数
        
        Returns:
            被包装函数的字典
        """
        return cls._wrapped_functions
    
    @classmethod
    def get_wrapped_function(cls, func_name: str) -> Optional[Dict[str, Any]]:
        """获取指定的被包装函数
        
        Args:
            func_name: 函数名称（格式：module.function）
        
        Returns:
            被包装函数的信息
        """
        return cls._wrapped_functions.get(func_name)

# 便捷装饰器
def redis_channel_listener(default_values: Dict[str, Any]) -> Callable:
    """Redis频道监听器装饰器
    
    Args:
        default_values: 要替换的默认值字典
    
    Returns:
        装饰器函数
    """
    wrapper = redisChannelListener(default_values)
    return wrapper
