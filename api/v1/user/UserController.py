from fastapi import APIRouter, Depends, Header

from model import Result
from model.common import JwtPayload
from model.dto.user import (ChangePasswordRequest, UpdateUserInfoRequest,
                            UserRegisterDTO)
from services import UserService, get_user_service
from utils.auth_utils import get_payload

user_router = APIRouter(prefix="/users", tags=["users"])

@user_router.post("", response_model=Result)
async def register(userRegisterDTO: UserRegisterDTO, user_service: UserService = Depends(get_user_service)):
    await user_service.register(userRegisterDTO)
    return Result.success()

@user_router.get("", response_model=Result)
async def me(payload: JwtPayload = Depends(get_payload), user_service: UserService = Depends(get_user_service)):
    user_id = int(payload.user_id)
    data = await user_service.get_user_info(user_id)
    return Result.success(data)

@user_router.put("", response_model=Result)
async def update_me(req: UpdateUserInfoRequest, payload: JwtPayload = Depends(get_payload), user_service: UserService = Depends(get_user_service)):
    user_id = int(payload.user_id)
    data = await user_service.update_user_info(user_id, req)
    return Result.success(data)

@user_router.put("/password", response_model=Result)
async def change_password(req: ChangePasswordRequest, payload: JwtPayload = Depends(get_payload), user_service: UserService = Depends(get_user_service)):
    user_id = int(payload.user_id)
    await user_service.change_password(user_id, req)
    return Result.success()
