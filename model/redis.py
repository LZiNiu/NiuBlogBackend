from typing import Optional, Generator
from contextlib import contextmanager

from core.config import settings

import redis


_redis_client: Optional[redis.Redis] = None


def init_redis() -> Optional[redis.Redis]:
    """
    在应用启动时初始化全局 Redis 客户端。
    """
    global _redis_client
    if redis is None or not settings.REDIS_URL:
        _redis_client = None
        return None
    if _redis_client is None:
        client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)  # type: ignore
        try:
            client.ping()
            _redis_client = client
        except Exception:
            _redis_client = None
    return _redis_client

def close_redis() -> None:
    """
    在应用关闭时释放 Redis 连接。
    """
    global _redis_client
    try:
        if _redis_client is not None:
            _redis_client.close()
            # 某些版本也可用: _redis_client.connection_pool.disconnect()
    finally:
        _redis_client = None

def get_redis_client() -> Optional[redis.Redis]:
    """
    获取全局 Redis 客户端；未配置或连接失败返回 None。
    """
    global _redis_client
    if _redis_client is None:
        # 如果尚未初始化，尝试初始化一次（兼容未通过 lifespan 的场景，例如单元测试）
        return init_redis()
    return _redis_client


@contextmanager
def get_redis_conn():
    """
    提供 Redis 客户端的上下文管理器（可能为 None）。
    使用方法:
    with get_redis_conn() as r:
        if r:
            r.set("key", "value")
    """
    client = get_redis_client()
    try:
        yield client
    finally:
        pass


def get_redis() -> Generator[Optional["redis.Redis"], None, None]:  # type: ignore
    """
    FastAPI 依赖注入用的 Redis 获取函数（可能为 None）。
    """
    client = get_redis_client()
    try:
        yield client
    finally:
        pass