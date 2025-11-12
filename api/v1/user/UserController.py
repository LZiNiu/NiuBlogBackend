from fastapi import APIRouter, HTTPException, Depends
from fastapi import Header
from model import Result
from services import get_user_service, UserService
from model.user import UserRegisterDTO, UserLoginRequest, UpdateUserInfoRequest, ChangePasswordRequest
from utils.auth_utils import validate_access_token, get_payload, get_token

user_router = APIRouter(prefix="/users", tags=["users"])

@user_router.post("", response_model=Result)
def register(userRegisterDTO: UserRegisterDTO, user_service: UserService = Depends(get_user_service)):
    user_service.register(userRegisterDTO)
    return Result.success()

@user_router.get("", response_model=Result)
def me(authorization: str = Header(...), user_service: UserService = Depends(get_user_service)):
    payload = get_payload(authorization)
    user_id = int(payload.user_id)  # type: ignore
    data = user_service.get_user_info(user_id)
    return Result.success(data)

@user_router.put("", response_model=Result)
def update_me(req: UpdateUserInfoRequest, authorization: str = Header(...), user_service: UserService = Depends(get_user_service)):
    payload = get_payload(authorization)
    user_id = int(payload.user_id)  # type: ignore
    data = user_service.update_user_info(user_id, req)
    return Result.success(data)

@user_router.put("/password", response_model=Result)
def change_password(req: ChangePasswordRequest, authorization: str = Header(...), user_service: UserService = Depends(get_user_service)):
    payload = get_payload(authorization)
    user_id = int(payload.user_id)  # type: ignore
    user_service.change_password(user_id, req)
    return Result.success()
