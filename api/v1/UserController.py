from fastapi import APIRouter, HTTPException, Depends
from model import User, UserRegisterDTO, Result
from services import get_user_service, UserService
from model.user import UserLoginRequest
from fastapi import Header

auth_router = APIRouter(prefix="/auth", tags=["auth"])
user_router = APIRouter(prefix="/users", tags=["users"])

@auth_router.post("/register", response_model=Result)
def register(userRegisterDTO: UserRegisterDTO,user_service: UserService = Depends(get_user_service)):
    user_service.register(userRegisterDTO)
    return Result.success()

@auth_router.post("/login", response_model=Result)
def login(loginRequest: UserLoginRequest, user_service: UserService = Depends(get_user_service)):
    resp = user_service.authenticate(loginRequest)
    return Result.success(resp)

@auth_router.post("/logout", response_model=Result)
def logout(authorization: str = Header(...), user_service: UserService = Depends(get_user_service)):
    # 从 Authorization: Bearer xxx 提取令牌
    token = authorization.removeprefix("Bearer").strip()
    user_service.logout(token)
    return Result.success()


