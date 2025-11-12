from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlmodel import SQLModel

from core.config import settings

# 创建数据库引擎
engine = create_engine(
    url=settings.DATABASE_URL,
    pool_size=10,           # 连接池大小
    max_overflow=20,        # 超出pool_size后最多可创建的连接数
    pool_pre_ping=True,     # 检查连接是否有效
    pool_recycle=3600,      # 连接回收时间(秒)
    echo=False              # 是否输出SQL语句(开发时可设为True)
)

# 创建SessionLocal类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)


# 获取数据库session的上下文管理器
@contextmanager
def get_db_session():
    """
    提供一个数据库session的上下文管理器
    使用方法:
    with get_db_session() as db:
        # 执行数据库操作
        pass
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


# 依赖注入用的数据库获取函数
def get_session() -> Generator[Session]:
    """
    FastAPI依赖注入用的数据库session获取函数
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
