from typing import Optional, Iterable

from fastapi import Request

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

from core.biz_constants import BizCode, BizMsg
from model.common import Result
from model.orm.models import Role
from utils.auth_utils import JwtUtil
from utils.user_context import UserContext, set_user_context, clear_user_context


def _starts_with(path: str, prefixes: Iterable[str]) -> bool:
    return any(path.startswith(p) for p in prefixes)


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        admin_prefixes: Optional[list[str]] = None,
        protected_prefixes: Optional[list[str]] = None,
        public_paths: Optional[list[str]] = None,
        protected_post_prefixes: Optional[list[str]] = None,
    ) -> None:
        super().__init__(app)
        self.admin_prefixes = admin_prefixes or ["/api/v1/admin"]
        # 需要登录但非管理员的路径前缀或具体路径
        self.protected_prefixes = protected_prefixes or [
            "/api/v1/users/bloguser",
            "/api/v1/auth/logout",
            "/api/v1/auth/password",
        ]
        # 仅在 POST 时需要登录的路径前缀（如发表评论）
        self.protected_post_prefixes = protected_post_prefixes or [
            "/api/v1/users/comment",
        ]
        # 明确公开路径（优先级最高）
        self.public_paths = public_paths or [
            "/api/v1/auth/login",
            "/api/v1/auth/refresh"
        ]

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path

        # 公开路径直接放行
        if path in self.public_paths:
            return await call_next(request)

        require_admin = _starts_with(path, self.admin_prefixes)
        require_user = _starts_with(path, self.protected_prefixes)
        if request.method.upper() == "POST" and _starts_with(path, self.protected_post_prefixes):
            require_user = True

        # 不需要鉴权的路径直接放行
        if not require_admin and not require_user:
            return await call_next(request)

        # 获取请求头中的Authorization字段
        auth = request.headers.get("Authorization")
        if not auth:
            # 未提供令牌
            return JSONResponse(status_code=401, content=Result.failure(
                                        msg=BizMsg.TOKEN_REQUIRED, code=BizCode.TOKEN_REQUIRED).model_dump())

        if auth.startswith("Bearer "):
            # 从Authorization字段中提取令牌
            token = auth.split(" ", 1)[1].strip()
        else:
            # 非Bearer格式, 认为直接传递了令牌
            token = auth

        payload = await JwtUtil.get_payload(token)
        if not payload:
            # 令牌无效
            return JSONResponse(status_code=401, content=Result.failure(
                                        msg=BizMsg.TOKEN_INVALID, code=BizCode.TOKEN_INVALID).model_dump())
        JwtUtil.logger.info(f"成功解析令牌 当前用户:{payload.user_id}, 权限级别: {payload.role}")
        # 管理员校验
        if require_admin and payload.role not in [Role.ADMIN.value, Role.SUPER.value]:
            return JSONResponse(
                content=Result.failure(msg=BizMsg.FORBIDDEN, code=BizCode.FORBIDDEN).model_dump(),
                status_code=403,
            )

        # 设置上下文并继续处理
        set_user_context(UserContext(
            user_id=payload.user_id,
            username=payload.username,
            role=payload.role,
            token=token
        ))
        try:
            response = await call_next(request)
            return response
        finally:
            clear_user_context()