from fastapi import APIRouter, Depends, Header, Security
from fastapi.security import HTTPAuthorizationCredentials

from model import Result
from model.dto.user import UserLoginRequest, ChangePasswordRequest, RefreshTokenRequest
from model.common import JwtPayload
from services import UserService, get_user_service

from utils.auth_utils import JwtUtil

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/login", response_model=Result)
async def login(loginRequest: UserLoginRequest, user_service: UserService = Depends(get_user_service)):
    resp = await user_service.authenticate(loginRequest)
    return Result.success(resp)

@auth_router.post("/logout", response_model=Result)
def logout(credentials: HTTPAuthorizationCredentials = Security(JwtUtil.security), user_service: UserService = Depends(get_user_service)):
    # 不涉及io等待, 不使用异步, fastapi会将其放入线程池中执行而不是事件循环
    # jwt的操作偏计算, 线程池中执行更高效
    token = credentials.credentials
    user_service.logout(token)
    return Result.success()


@auth_router.put("/password", response_model=Result)
async def change_password(req: ChangePasswordRequest, 
                            payload: JwtPayload = Depends(JwtUtil.get_payload), 
                            user_service: UserService = Depends(get_user_service)):
    user_id = int(payload.user_id)
    await user_service.change_password(user_id, req)
    return Result.success()

@auth_router.post("/refresh", response_model=Result)
def refresh_tokens(req: RefreshTokenRequest, user_service: UserService = Depends(get_user_service)):
    data = user_service.refresh_tokens(req.refreshToken)
    return Result.success(data)
