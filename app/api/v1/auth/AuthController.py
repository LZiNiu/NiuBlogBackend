from fastapi import APIRouter, Depends

from app.model import Result
from app.model.dto.user import UserLoginRequest, ChangePasswordRequest
from app.model.vo.auth import RefreshTokenRequest
from app.core import BizCode, BizMsg
from app.services import UserService, get_user_service
from app.utils.user_context import get_user_context

auth_router = APIRouter(prefix="/auth", tags=["认证接口"])

@auth_router.post("/login", response_model=Result)
async def login(loginRequest: UserLoginRequest, user_service: UserService = Depends(get_user_service)):
    resp = await user_service.authenticate(loginRequest)
    return Result.success(resp)

@auth_router.post("/logout", response_model=Result)
def logout(user_service: UserService = Depends(get_user_service)):
    ctx = get_user_context()
    if not ctx:
        return Result.failure(msg=BizMsg.TOKEN_REQUIRED, code=BizCode.TOKEN_REQUIRED)
    user_service.logout(ctx.token)
    return Result.success()


@auth_router.put("/password", response_model=Result)
async def change_password(req: ChangePasswordRequest, user_service: UserService = Depends(get_user_service)):
    ctx = get_user_context()
    if not ctx:
        return Result.failure(msg=BizMsg.TOKEN_REQUIRED, code=BizCode.TOKEN_REQUIRED)
    user_id = int(ctx.user_id)
    await user_service.change_password(user_id, req)
    return Result.success()

@auth_router.post("/refresh", response_model=Result)
def refresh_tokens(req: RefreshTokenRequest, user_service: UserService = Depends(get_user_service)):
    data = user_service.refresh_tokens(req.refreshToken)
    return Result.success(data)
