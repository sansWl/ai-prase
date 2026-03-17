import asyncio
from factories.threadFactory.redis_channel import redis_channel_listener,redisChannelListener
from utils.redisUtils import consumer_task
from utils import logger

@redis_channel_listener({'channel': 'test_channel'})
def listen_test_channel(channel: str):
    """Redis频道监听器
    subscribe redis pubsub channel
    Args:
        channel: 要监听的Redis频道
    """
    consumer_task(channel)

@redis_channel_listener({'channel': 'demo_channel'})
def listen_demo_channel(channel: str):
    """Redis频道监听器
    subscribe redis pubsub channel
    Args:
        channel: 要监听的Redis频道
    """
    consumer_task(channel)

async def run_function(func, default_values):
    """在线程池中运行阻塞函数"""
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, lambda: func(**default_values))


async def start_listeners():
    """启动所有 Redis 监听器（后台协程）"""
    logger.info("Redis频道监听器开始启动")
    res = redisChannelListener._wrapped_functions
    for fun_name, func_info in res.items():
        func = func_info['function']
        default_values = func_info['default_values']
        # 创建后台协程任务
        asyncio.create_task(run_function(func, default_values))
        print(f"为函数 {fun_name} 创建后台协程")
    
    logger.info("Redis频道监听器后台协程已全部启动")
    



