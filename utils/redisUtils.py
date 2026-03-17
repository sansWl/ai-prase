from utils import logger
from middleware.redis_client import get_redis_client
from typing import Optional, List
from info import queue_event

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


def producer_task(key: str, queue_name: str, queue_task: queue_event.QueueEvent, task_data: List[str]):
    """生产任务到 Redis 队列"""
    return redis_client.producer_task(key, queue_name, queue_task.to_json(), task_data)


def consumer_task(queue_name: str, timeout: int = None):
    """从 Redis 队列消费任务"""
    return  redis_client.consumer_task(queue_name, timeout)
