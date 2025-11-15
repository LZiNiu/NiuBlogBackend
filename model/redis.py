import redis.asyncio as redis
from redis.asyncio.client import Redis
from typing import Optional
from core.config import settings


class RedisClientManager:
    """
    生产级 Redis 客户端管理器：
    - 单例连接池
    - 自动初始化/关闭
    - 获取共享 Redis 客户端
    """
    _redis_client: Optional[Redis] = None

    @classmethod
    async def init(cls) -> None:
        """初始化连接池（FastAPI startup 调用）"""
        if cls._redis_client is None:
            conn_pool = redis.ConnectionPool(
                max_connections=settings.redis.POOL_SIZE,
            )
            cls._redis_client = redis.Redis(connection_pool=conn_pool,
                    host=settings.redis.HOST,
                    port=settings.redis.PORT,
                    db=settings.redis.DB,
                    password=settings.redis.PASSWORD,
                    decode_responses=True,  # 自动解码 str
                    socket_timeout=1,  # 1秒超时
                    socket_connect_timeout=2,  # 2秒连接超时
                )
            # 测试连接
            try:
                await cls._redis_client.ping()
            except redis.ConnectionError:
                raise RuntimeError("Failed to connect to Redis server")

    @classmethod
    def get_client(cls) -> Redis:
        """获取 Redis 实例（确保 init 后使用）"""
        if cls._redis_client is None:
            raise RuntimeError("Redis client not initialized")
        return cls._redis_client

    @classmethod
    async def close(cls) -> None:
        """关闭连接池（FastAPI shutdown 调用）"""
        if cls._redis_client:
            await cls._redis_client.close()
            cls._redis_client = None


# 给 FastAPI 依赖注入使用
async def get_redis() -> Redis:
    return RedisClientManager.get_client()
