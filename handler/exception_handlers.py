from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from utils.logger import setup_logging

# 获取 FastAPI 日志记录器
logger = setup_logging("exception_hanlder")

class CattleBlogException(Exception):
    """自定义异常基类"""
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class UserNotFoundException(CattleBlogException):
    """用户未找到异常"""
    def __init__(self, message: str = "用户未找到"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ArticleNotFoundException(CattleBlogException):
    """文章未找到异常"""
    def __init__(self, message: str = "文章未找到"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class AuthenticationException(CattleBlogException):
    """认证异常"""
    def __init__(self, message: str = "认证失败"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class AuthorizationException(CattleBlogException):
    """授权异常"""
    def __init__(self, message: str = "权限不足"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


def register_exception_handlers(app: FastAPI):
    """注册全局异常处理器"""
    
    @app.exception_handler(CattleBlogException)
    async def cattleblog_exception_handler(request: Request, exc: CattleBlogException):
        """处理自定义异常"""
        logger.error(f"CattleBlogException: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code,
                "message": exc.message,
                "data": None
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """处理请求验证异常"""
        logger.error(f"RequestValidationError: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": "请求参数验证失败",
                "data": {"details": exc.errors()}
            }
        )
    
    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
        """处理Pydantic模型验证异常"""
        logger.error(f"Pydantic ValidationError: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": "数据验证失败",
                "data": {"details": exc.errors()}
            }
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """处理fastapi自带的HTTP异常"""
        logger.error(f"HTTPException: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code,
                "message": exc.detail,
                "data": None
            }
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """处理未捕获的异常"""
        logger.error(f"Global Exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "服务器内部错误",
                "data": None
            }
        )