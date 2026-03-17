import os
import json
import redis
from typing import Optional, Union, List, Any
from dotenv import load_dotenv
from utils import logger

load_dotenv()


class RedisClient:
    """Redis 客户端封装类"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._client = None
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._init_client()
    
    def _init_client(self):
        """初始化 Redis 连接"""
        host = os.getenv('REDIS_HOST', 'localhost')
        port = int(os.getenv('REDIS_PORT', 6379))
        password = os.getenv('REDIS_PASSWORD', None)
        db = int(os.getenv('REDIS_DB', 0))
        
        try:
            self._client = redis.Redis(
                host=host,
                port=port,
                password=password,
                db=db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                health_check_interval=30
            )
            # 测试连接
            self._client.ping()
            logger.info(f"Redis 连接成功: {host}:{port}")
        except redis.ConnectionError as e:
            logger.error(f"Redis 连接失败: {e}")
            self._client = None
        except Exception as e:
            logger.error(f"Redis 初始化错误: {e}")
            self._client = None
    
    def get_client(self) -> Optional[redis.Redis]:
        """获取 Redis 客户端实例"""
        if self._client is None:
            self._init_client()
        return self._client
    
    def is_connected(self) -> bool:
        """检查是否已连接"""
        if self._client is None:
            return False
        try:
            return self._client.ping()
        except:
            return False
    
    # ==================== 字符串操作 ====================
    
    def set(self, key: str, value: Union[str, int, float, dict, list], 
            expire: Optional[int] = None) -> bool:
        """
        设置键值对
        
        Args:
            key: 键名
            value: 值（支持字符串、数字、字典、列表）
            expire: 过期时间（秒）
        
        Returns:
            是否设置成功
        """
        if self._client is None:
            return False
        
        try:
            # 处理复杂类型
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            if expire:
                return self._client.setex(key, expire, value)
            else:
                return self._client.set(key, value)
        except Exception as e:
            logger.error(f"Redis set 错误: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取键值
        
        Args:
            key: 键名
            default: 默认值
        
        Returns:
            键值或默认值
        """
        if self._client is None:
            return default
        
        try:
            value = self._client.get(key)
            if value is None:
                return default
            
            # 尝试解析 JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Redis get 错误: {e}")
            return default
    
    def delete(self, key: str) -> bool:
        """删除键"""
        if self._client is None:
            return False
        
        try:
            return self._client.delete(key) > 0
        except Exception as e:
            logger.error(f"Redis delete 错误: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if self._client is None:
            return False
        
        try:
            return self._client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis exists 错误: {e}")
            return False
    
    def expire(self, key: str, seconds: int) -> bool:
        """设置键的过期时间"""
        if self._client is None:
            return False
        
        try:
            return self._client.expire(key, seconds)
        except Exception as e:
            logger.error(f"Redis expire 错误: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """获取键的剩余过期时间"""
        if self._client is None:
            return -2
        
        try:
            return self._client.ttl(key)
        except Exception as e:
            logger.error(f"Redis ttl 错误: {e}")
            return -2
    
    # ==================== 哈希操作 ====================
    
    def hset(self, name: str, key: str, value: Any) -> bool:
        """设置哈希字段"""
        if self._client is None:
            return False
        
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            return self._client.hset(name, key, value)
        except Exception as e:
            logger.error(f"Redis hset 错误: {e}")
            return False
    
    def hget(self, name: str, key: str, default: Any = None) -> Any:
        """获取哈希字段"""
        if self._client is None:
            return default
        
        try:
            value = self._client.hget(name, key)
            if value is None:
                return default
            
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Redis hget 错误: {e}")
            return default
    
    def hgetall(self, name: str) -> dict:
        """获取所有哈希字段"""
        if self._client is None:
            return {}
        
        try:
            result = self._client.hgetall(name)
            # 尝试解析 JSON 值
            parsed = {}
            for k, v in result.items():
                try:
                    parsed[k] = json.loads(v)
                except (json.JSONDecodeError, TypeError):
                    parsed[k] = v
            return parsed
        except Exception as e:
            logger.error(f"Redis hgetall 错误: {e}")
            return {}
    
    def hdel(self, name: str, key: str) -> bool:
        """删除哈希字段"""
        if self._client is None:
            return False
        
        try:
            return self._client.hdel(name, key) > 0
        except Exception as e:
            logger.error(f"Redis hdel 错误: {e}")
            return False
    
    # ==================== 列表操作 ====================
    
    def lpush(self, name: str, *values) -> int:
        """从左侧推入列表"""
        if self._client is None:
            return 0
        
        try:
            values = [json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v 
                     for v in values]
            return self._client.lpush(name, *values)
        except Exception as e:
            logger.error(f"Redis lpush 错误: {e}")
            return 0
    
    def rpush(self, name: str, *values) -> int:
        """从右侧推入列表"""
        if self._client is None:
            return 0
        
        try:
            values = [json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v 
                     for v in values]
            return self._client.rpush(name, *values)
        except Exception as e:
            logger.error(f"Redis rpush 错误: {e}")
            return 0
    
    def lrange(self, name: str, start: int = 0, end: int = -1) -> list:
        """获取列表范围"""
        if self._client is None:
            return []
        
        try:
            values = self._client.lrange(name, start, end)
            result = []
            for v in values:
                try:
                    result.append(json.loads(v))
                except (json.JSONDecodeError, TypeError):
                    result.append(v)
            return result
        except Exception as e:
            logger.error(f"Redis lrange 错误: {e}")
            return []
    
    def lpop(self, name: str) -> Any:
        """从左侧弹出"""
        if self._client is None:
            return None
        
        try:
            value = self._client.lpop(name)
            if value is None:
                return None
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Redis lpop 错误: {e}")
            return None
    
    def rpop(self, name: str) -> Any:
        """从右侧弹出"""
        if self._client is None:
            return None
        
        try:
            value = self._client.rpop(name)
            if value is None:
                return None
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Redis rpop 错误: {e}")
            return None
    
    # ==================== 集合操作 ====================
    
    def sadd(self, name: str, *values) -> int:
        """添加集合成员"""
        if self._client is None:
            return 0
        
        try:
            values = [json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v) 
                     for v in values]
            return self._client.sadd(name, *values)
        except Exception as e:
            logger.error(f"Redis sadd 错误: {e}")
            return 0
    
    def smembers(self, name: str) -> set:
        """获取集合所有成员"""
        if self._client is None:
            return set()
        
        try:
            members = self._client.smembers(name)
            result = set()
            for m in members:
                try:
                    result.add(json.loads(m))
                except (json.JSONDecodeError, TypeError):
                    result.add(m)
            return result
        except Exception as e:
            logger.error(f"Redis smembers 错误: {e}")
            return set()
    
    def sismember(self, name: str, value: Any) -> bool:
        """检查是否是集合成员"""
        if self._client is None:
            return False
        
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            return self._client.sismember(name, value)
        except Exception as e:
            logger.error(f"Redis sismember 错误: {e}")
            return False
    
    def srem(self, name: str, *values) -> int:
        """移除集合成员"""
        if self._client is None:
            return 0
        
        try:
            values = [json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v) 
                     for v in values]
            return self._client.srem(name, *values)
        except Exception as e:
            logger.error(f"Redis srem 错误: {e}")
            return 0
    
    # ==================== 分布式锁 ====================
    
    def acquire_lock(self, lock_name: str, acquire_timeout: int = 10, 
                     lock_timeout: int = 10) -> Optional[str]:
        """
        获取分布式锁
        
        Args:
            lock_name: 锁名称
            acquire_timeout: 获取锁的超时时间（秒）
            lock_timeout: 锁的过期时间（秒）
        
        Returns:
            锁标识符或 None
        """
        if self._client is None:
            return None
        
        import time
        import uuid
        
        identifier = str(uuid.uuid4())
        lock_key = f"lock:{lock_name}"
        end_time = time.time() + acquire_timeout
        
        while time.time() < end_time:
            if self._client.setnx(lock_key, identifier):
                self._client.expire(lock_key, lock_timeout)
                return identifier
            elif self._client.ttl(lock_key) == -1:
                self._client.expire(lock_key, lock_timeout)
            
            time.sleep(0.001)
        
        return None
    
    def release_lock(self, lock_name: str, identifier: str) -> bool:
        """
        释放分布式锁
        
        Args:
            lock_name: 锁名称
            identifier: 锁标识符
        
        Returns:
            是否释放成功
        """
        if self._client is None:
            return False
        
        lock_key = f"lock:{lock_name}"
        
        # 使用 Lua 脚本确保原子性
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        try:
            result = self._client.eval(lua_script, 1, lock_key, identifier)
            return result == 1
        except Exception as e:
            logger.error(f"Redis release_lock 错误: {e}")
            return False
    
    # ==================== 键管理 ====================
    
    def keys(self, pattern: str = "*") -> list:
        """查找键"""
        if self._client is None:
            return []
        
        try:
            return list(self._client.scan_iter(match=pattern))
        except Exception as e:
            logger.error(f"Redis keys 错误: {e}")
            return []
    
    def flushdb(self) -> bool:
        """清空当前数据库"""
        if self._client is None:
            return False
        
        try:
            return self._client.flushdb()
        except Exception as e:
            logger.error(f"Redis flushdb 错误: {e}")
            return False
    
    def close(self):
        """关闭连接"""
        if self._client is not None:
            self._client.close()
            self._client = None
            logger.info("Redis 连接已关闭")

    # ==================== pub/sub ====================

    def producer_task(self, key:str, channel: str, queue_task: str, message: Union[str, List[str]]):
        """发布消息到频道"""
        if self._client is None:
            logger.error("Redis 客户端未初始化")
            return
        
        try:
            
            # 确保 message 是列表
            if isinstance(message, str):
                message = [message]
            
            # 构建Lua脚本
            lua_script = """
            local channel = KEYS[1]
            local key = KEYS[2]
            local queue_task = ARGV[1]
            
            -- 从ARGV[2]开始处理消息
            for i = 2, #ARGV do
                redis.call('LPUSH', key, ARGV[i])
            end
            
            -- 发布通知
            redis.call("publish", channel, queue_task)
            """
            
            # 构建参数列表
            args = [channel, key, queue_task]
            args.extend(message)
            
            # 执行Lua脚本
            self._client.eval(lua_script, 2, *args)
        except Exception as e:
            logger.error(f"Redis publish 错误: {e}")
    
    def consumer_task(self, key: str, timeout: int = None):
        """从队列消费任务
        key: 队列名称
        timeout: 超时时间（秒）
        """
        if self._client is None:
            logger.error("Redis 客户端未初始化")
            return None
        
        try:
            # 从列表右侧弹出元素（FIFO队列）
            pubsub = self._client.pubsub()
            pubsub.subscribe(key)
            for message in pubsub.listen():
                logger.info(f"消费消息: {message}")
                if message['type'] == 'message':
                    return message['data'].decode('utf-8')
            return None
        except Exception as e:
            logger.error(f"Redis consumer 错误: {e}")
            return None

# 全局 Redis 客户端实例
redis_client = RedisClient()


def get_redis_client() -> RedisClient:
    """获取 Redis 客户端实例"""
    return redis_client
