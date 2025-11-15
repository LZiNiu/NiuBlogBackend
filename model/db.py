from typing import AsyncGenerator
from urllib.parse import urlsplit, urlunsplit

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine, AsyncEngine
import importlib.util as _iu
from core.config import settings


def _to_async_url(url: str) -> str:
    parts = urlsplit(url)
    scheme = parts.scheme
    if scheme.startswith("sqlite"):
        async_scheme = "sqlite+aiosqlite"
    elif scheme.startswith("postgresql") or scheme.startswith("postgres"):
        async_scheme = "postgresql+asyncpg"
    elif scheme.startswith("mysql"):
        if _iu.find_spec("aiomysql") is not None:
            async_scheme = "mysql+aiomysql"
        elif _iu.find_spec("asyncmy") is not None:
            async_scheme = "mysql+asyncmy"
        else:
            async_scheme = "mysql+aiomysql"
    else:
        async_scheme = scheme
    return urlunsplit((async_scheme, parts.netloc, parts.path, parts.query, parts.fragment))


# 创建异步数据库引擎（惰性创建，避免导入时缺少驱动导致失败）
ASYNC_DATABASE_URL = _to_async_url(settings.db.URL)
engine: AsyncEngine | None = None
SessionLocal: async_sessionmaker[AsyncSession] | None = None

def _ensure_engine() -> AsyncEngine:
    global engine, SessionLocal
    if engine is None:
        engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)
        SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    return engine


# FastAPI 依赖注入：异步会话
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    _ensure_engine()
    assert SessionLocal is not None
    async with SessionLocal() as session:
        yield session
