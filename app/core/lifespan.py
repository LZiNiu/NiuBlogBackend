from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging

from app.db.redis import RedisClientManager
from app.db.session import close_db
from app.utils.logger import cleanup_logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动：初始化 Redis 连接
    await RedisClientManager.init()
    yield
    # 应用关闭：释放 Redis 连接
    await RedisClientManager.close()
    await close_db()
    # 清理日志记录器
    cleanup_logging()
