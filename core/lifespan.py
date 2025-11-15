from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging

from model.redis import RedisClientManager
from model.db import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 尝试禁用 uvicorn.error 日志记录器
    uvicorn_error_logger = logging.getLogger("uvicorn.error")
    uvicorn_error_logger.disabled = True
    # 应用启动：初始化 Redis 连接
    await RedisClientManager.init()
    yield
    # 应用关闭：释放 Redis 连接
    await RedisClientManager.close()
    if engine is not None:
        await engine.dispose()
