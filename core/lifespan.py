from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.config import settings
import logging

from model.redis import init_redis, close_redis
from model.db import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 尝试禁用 uvicorn.error 日志记录器
    uvicorn_error_logger = logging.getLogger("uvicorn.error")
    uvicorn_error_logger.disabled = True
    # 应用启动：初始化 Redis 连接
    init_redis()
    yield
    # 应用关闭：释放 Redis 连接
    close_redis()
    if engine is not None:
        engine.dispose()
