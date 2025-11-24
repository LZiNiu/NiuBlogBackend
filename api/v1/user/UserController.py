from fastapi import APIRouter, Depends, UploadFile, File

from model import Result
from core.biz_constants import BizCode, BizMsg
from model.dto.user import (UpdateUserInfoRequest,
                            UserRegisterDTO)
from services import UserService, get_user_service
from utils.user_context import get_user_context
from utils.upload import save_avatar

router = APIRouter(prefix="/bloguser", tags=["blog-user"])

@router.post("", response_model=Result)
async def register(userRegisterDTO: UserRegisterDTO, user_service: UserService = Depends(get_user_service)):
    await user_service.register(userRegisterDTO)
    return Result.success()

@router.get("", response_model=Result)
async def me(user_service: UserService = Depends(get_user_service)):
    ctx = get_user_context()
    if not ctx:
        return Result.failure(msg=BizMsg.TOKEN_REQUIRED, code=BizCode.TOKEN_REQUIRED)
    user_id = int(ctx.user_id)
    data = await user_service.get_user_info(user_id)
    return Result.success(data)

@router.put("", response_model=Result)
async def update_me(req: UpdateUserInfoRequest, user_service: UserService = Depends(get_user_service)):
    ctx = get_user_context()
    if not ctx:
        return Result.failure(msg=BizMsg.TOKEN_REQUIRED, code=BizCode.TOKEN_REQUIRED)
    user_id = int(ctx.user_id)
    data = await user_service.update_user_info(user_id, req)
    return Result.success(data)

@router.post("/me/avatar", response_model=Result)
async def upload_avatar(file: UploadFile = File(...), user_service: UserService = Depends(get_user_service)):
    ctx = get_user_context()
    if not ctx:
        return Result.failure(msg=BizMsg.TOKEN_REQUIRED, code=BizCode.TOKEN_REQUIRED)
    user_id = int(ctx.user_id)
    content = await file.read()
    _, rel = save_avatar(content, file.filename or "avatar", user_id)
    data = await user_service.update_user_info(user_id, UpdateUserInfoRequest(avatar_url=rel))
    return Result.success({"avatar_url": rel, "user": data})
