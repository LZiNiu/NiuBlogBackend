from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine, AsyncEngine
from app.core import settings

ASYNC_DATABASE_URL = settings.db.ASYNC_DB_URI
engine: AsyncEngine | None = None
SessionLocal: async_sessionmaker[AsyncSession] | None = None

def _ensure_engine() -> AsyncEngine:
    global engine, SessionLocal
    if engine is None:
        engine = create_async_engine(ASYNC_DATABASE_URL, echo=settings.db.ECHO)
        SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    return engine


# FastAPI 依赖注入：异步会话
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    _ensure_engine()
    assert SessionLocal is not None
    async with SessionLocal() as session:
        yield session


async def close_db() -> None:
    """关闭数据库连接"""
    global engine
    if engine is not None:
        await engine.dispose()