from typing import Generic, Optional, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase

T = TypeVar('T')

class Base(DeclarativeBase):
    pass


class Result(BaseModel, Generic[T]):
    """统一响应包装类"""
    code: int
    msg: str
    data: Optional[T] = None

    @classmethod
    def success(cls, data: Optional[T] = None, msg: str = "success", code: int = 200) -> "Result[T]":
        """成功响应"""
        return cls(code=code, msg=msg, data=data)

    @classmethod
    def failure(cls, msg: str = "error", code: int = 500, data: Optional[T] = None) -> "Result[T]":
        """失败响应"""
        return cls(code=code, msg=msg, data=data)


class JwtPayload(BaseModel):
    """JWT 载荷模型"""
    user_id: int | str
    username: str
    role: str

class PagedVO(BaseModel):
    """分页响应 DTO（如需直接使用可保留），推荐使用 Result.page"""
    total: int
    current: int
    size: int
    records: list