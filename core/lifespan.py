from contextlib import asynccontextmanager
from fastapi import FastAPI

from model.redis import init_redis, close_redis
from model.db import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动：初始化 Redis 连接
    init_redis()
    yield
    # 应用关闭：释放 Redis 连接
    close_redis()
    engine.dispose()
