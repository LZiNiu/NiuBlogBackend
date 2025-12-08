from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.utils.logger import setup_logging
from app.core import BizCode, BizMsg

# 获取 FastAPI 日志记录器
logger = setup_logging("exception_hanlder")

class CattleBlogException(Exception):
    def __init__(self, msg: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR, biz_code: int = BizCode.ERROR):
        self.msg = msg
        self.status_code = status_code
        self.biz_code = biz_code
        super().__init__(self.msg)


class UserNotFoundException(CattleBlogException):
    def __init__(self, msg: str = BizMsg.USER_NOT_FOUND):
        super().__init__(msg, status.HTTP_404_NOT_FOUND, BizCode.USER_NOT_FOUND)


class ArticleNotFoundException(CattleBlogException):
    def __init__(self, msg: str = BizMsg.ARTICLE_NOT_FOUND):
        super().__init__(msg, status.HTTP_404_NOT_FOUND, BizCode.ARTICLE_NOT_FOUND)


class AuthenticationException(CattleBlogException):
    def __init__(self, msg: str = BizMsg.TOKEN_INVALID, biz_code: int = BizCode.TOKEN_INVALID):
        super().__init__(msg, status.HTTP_401_UNAUTHORIZED, biz_code=BizCode.VALIDATION_ERROR)


class AuthorizationException(CattleBlogException):
    def __init__(self, msg: str = BizMsg.FORBIDDEN):
        super().__init__(msg, status.HTTP_403_FORBIDDEN, BizCode.FORBIDDEN)


def register_exception_handlers(app: FastAPI):
    """注册全局异常处理器"""
    
    @app.exception_handler(CattleBlogException)
    async def cattleblog_exception_handler(request: Request, exc: CattleBlogException):
        logger.error(f"CattleBlogException: {exc.msg}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.biz_code,
                "msg": exc.msg,
                "data": None
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"RequestValidationError: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "code": BizCode.VALIDATION_ERROR,
                "msg": BizMsg.VALIDATION_ERROR,
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
                "msg": "数据验证失败",
                "data": {exc.errors()}
            }
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.error(f"HTTPException: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": BizCode.ERROR,
                "msg": str(exc.detail),
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
                "msg": "服务器内部错误",
                "data": None
            }
        )