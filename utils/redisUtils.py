from middleware.redis_client import get_redis_client
from typing import Optional

redis_client = get_redis_client()

def set_redis_key(key: str, value: str, expire: int = None):
    """设置 Redis 键值对"""
    
    return redis_client.set(key, value, expire)

def get_redis_key(key: str, default=None):
    """获取 Redis 键值"""
    return redis_client.get(key, default)

def delete_redis_key(key: str):
    """删除 Redis 键"""
    return redis_client.delete(key)

def acquire_redis_lock(lock_key: str, acquire_timeout: int = 15, lock_timeout: int = 15) -> Optional[str]:
    """尝试获取 Redis 锁"""
    return redis_client.acquire_lock(lock_key, acquire_timeout, lock_timeout)
    
def release_redis_lock(lock_key: str, identifier: str) -> bool:
    """释放 Redis 锁"""
    return redis_client.release_lock(lock_key, identifier)

    