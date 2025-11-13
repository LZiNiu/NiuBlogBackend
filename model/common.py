
from typing import Optional, Generic, TypeVar
from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase

T = TypeVar('T')

class Base(DeclarativeBase):
    pass


class Result(BaseModel, Generic[T]):
    """统一响应包装类"""
    code: int
    message: str
    data: Optional[T] = None

    @classmethod
    def success(cls, data: Optional[T] = None, message: str = "success", code: int = 200) -> "Result[T]":
        """成功响应"""
        return cls(code=code, message=message, data=data)

    @classmethod
    def failure(cls, message: str = "error", code: int = 500, data: Optional[T] = None) -> "Result[T]":
        """失败响应"""
        return cls(code=code, message=message, data=data)


class JwtPayload(BaseModel):
    """JWT 载荷模型"""
    user_id: int | str
    username: str
    role: str

class PagedVO(BaseModel):
    """分页响应 DTO（如需直接使用可保留），推荐使用 Result.page"""
    total: int
    page: int
    size: int
    items: list