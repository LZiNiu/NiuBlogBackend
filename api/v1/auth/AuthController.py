from fastapi import APIRouter, Depends

from model import Result
from model.dto.user import UserLoginRequest, ChangePasswordRequest
from model.vo.auth import RefreshTokenRequest
from core.biz_constants import BizCode, BizMsg
from model.vo.user import UserInfoVO
from services import UserService, get_user_service

from utils.user_context import get_user_context

auth_router = APIRouter(prefix="/auth", tags=["auth"])

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
