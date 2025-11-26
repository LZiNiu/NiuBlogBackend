from typing import Generic, Optional, TypeVar

from pydantic import BaseModel
from core.biz_constants import BizCode, BizMsg
from sqlalchemy.orm import DeclarativeBase

T = TypeVar('T')

class Base(DeclarativeBase):
    pass


class Result(BaseModel, Generic[T]):
    code: int
    msg: str
    data: Optional[T] = None

    @classmethod
    def success(cls, data: Optional[T] = None, msg: str = BizMsg.SUCCESS, code: int = 200) -> "Result[T]":
        return cls(code=code, msg=msg, data=data)

    @classmethod
    def failure(cls, msg: str = BizMsg.ERROR, code: int = 200, data: Optional[T] = None) -> "Result[T]":
        return cls(code=code, msg=msg, data=data)


class JwtPayload(BaseModel):
    """JWT 载荷模型"""
    user_id: int | str
    username: str
    role: str

class PageQuery(BaseModel):
    """分页查询参数"""
    current: int = 1
    size: int = 5

class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应 vo"""
    total: int
    current: int
    size: int
    records: list[T]