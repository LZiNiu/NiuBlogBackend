from contextlib import contextmanager
from typing import Generator

from sqlmodel import create_engine, Session

from core.config import settings

# 创建数据库引擎
engine = create_engine(
    url=settings.DATABASE_URL,
    pool_size=10,           # 连接池大小
    max_overflow=20,        # 超出pool_size后最多可创建的连接数
    pool_pre_ping=True,     # 检查连接是否有效
    pool_recycle=3600,      # 连接回收时间(秒)
    echo=True,              # 是否输出SQL语句(开发时可设为True)
)

# 依赖注入用的数据库获取函数
def get_session() -> Generator[Session]:
    """
    FastAPI依赖注入用的数据库session获取函数
    """
    with Session(engine) as session:
        yield session
