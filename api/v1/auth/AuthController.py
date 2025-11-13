from fastapi import APIRouter, Depends, Header, Security
from fastapi.security import HTTPAuthorizationCredentials

from model import Result
from model.dto.user import UserLoginRequest
from services import UserService, get_user_service

from utils.auth_utils import _security

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/login", response_model=Result)
async def login(loginRequest: UserLoginRequest, user_service: UserService = Depends(get_user_service)):
    resp = await user_service.authenticate(loginRequest)
    return Result.success(resp)

@auth_router.post("/logout", response_model=Result)
async def logout(credentials: HTTPAuthorizationCredentials = Security(_security), user_service: UserService = Depends(get_user_service)):
    token = credentials.credentials
    await user_service.logout(token)
    return Result.success()
