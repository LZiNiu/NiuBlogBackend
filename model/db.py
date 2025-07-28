from sqlmodel import create_engine, Session, SQLModel
from core.config import settings
from . import models
from typing import Iterator

# 创建数据库引擎
try:
    engine = create_engine(settings.DATABASE_URL, echo=True)
except Exception as e:
    print("数据库连接失败!")
    raise e


# engine = create_engine(settings.DATABASE_URL)

# 获取数据库会话
def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
