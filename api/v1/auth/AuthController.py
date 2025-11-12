from fastapi import APIRouter, Depends
from fastapi import Header, Query
from model import Result
from services import get_user_service, UserService
from model.user import AdminCreateUserRequest, UserLoginRequest
from utils.auth_utils import get_token
from core.config import settings

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/login", response_model=Result)
def login(loginRequest: UserLoginRequest, user_service: UserService = Depends(get_user_service)):
    resp = user_service.authenticate(loginRequest)
    return Result.success(resp)

@auth_router.post("/logout", response_model=Result)
def logout(authorization: str = Header(...), user_service: UserService = Depends(get_user_service)):
    token = get_token(authorization)
    user_service.logout(token)
    return Result.success()