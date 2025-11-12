
from typing import Optional, Generic, TypeVar
from pydantic import BaseModel


T = TypeVar('T')

class Result(BaseModel, Generic[T]):
    """统一响应包装类"""
    success: bool
    code: int
    message: str
    data: Optional[T] = None

    @classmethod
    def success(cls, data: Optional[T] = None, message: str = "success", code: int = 200) -> "Result[T]":
        """成功响应"""
        return cls(success=True, code=code, message=message, data=data)

    @classmethod
    def failure(cls, message: str = "error", code: int = 500, data: Optional[T] = None) -> "Result[T]":
        """失败响应"""
        return cls(success=False, code=code, message=message, data=data)


class PagedVO(BaseModel):
    """分页响应 DTO（如需直接使用可保留），推荐使用 Result.page"""
    total: int
    page: int
    size: int
    items: list