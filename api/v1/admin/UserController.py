from uuid import uuid4
from fastapi import APIRouter, Depends, Header, HTTPException, Query, UploadFile, File
from core.config import settings
from model.common import Result
from model.dto.user import AdminCreateUserRequest, UpdateUserInfoRequest
from model.common import PagedVO
from model.vo.user import UserInfoVO
from services import UserService, get_user_service
from utils.user_context import get_user_context
from utils.upload import upload_image_to_qiniu
from core.biz_constants import BizMsg, BizCode
from model.dto.user import UpdateUserStatus
from fastapi import status

# admin路由添加鉴权拦截
router = APIRouter(prefix="/users", tags=["管理端用户管理"])

@router.get("/info", response_model=Result[UserInfoVO])
async def fetch_user_info(user_service: UserService = Depends(get_user_service)):
    ctx = get_user_context()
    if not ctx:
        return Result.failure(msg=BizMsg.TOKEN_REQUIRED, code=BizCode.TOKEN_REQUIRED)
    user_id = int(ctx.user_id)
    user = await user_service.get_user_info(user_id)
    return Result.success(user)

@router.get("", response_model=Result[PagedVO])
async def paginate_users_info(current: int = Query(1, ge=1), size: int = Query(10, ge=1, le=10), 
            user_service: UserService = Depends(get_user_service)):
    # 管理员分页查询所有用户信息
    items, total = await user_service.paginate_users_vo(current, size)
    return Result.success({"total": total, "current": current, "size": size, "records": items})

@router.get("/{user_id}", response_model=Result)
async def get_user_by_id(user_id: int, user_service: UserService = Depends(get_user_service)):
    data = await user_service.get_user_by_id(user_id)
    return Result.success(data)

@router.put("/{user_id}/status", response_model=Result)
async def update_status(user_id: int, status: UpdateUserStatus,
                        user_service: UserService = Depends(get_user_service)):
    data = await user_service.update_user_status(user_id, status)
    return Result.success(data)

@router.delete("/{user_id}", response_model=Result)
async def delete_user(user_id: int, 
                        user_service: UserService = Depends(get_user_service)):
    # 不允许删除超级管理员
    if user_id == settings.app.SUPER_ADMIN_USER_ID:
        raise HTTPException(status_code=403, detail="无权删除超级管理员")
    await user_service.delete_user(user_id)
    return Result.success()

@router.post("", response_model=Result)
async def create_user(req: AdminCreateUserRequest, user_service: UserService = Depends(get_user_service)):
    data = await user_service.admin_create_user(req)
    return Result.success(data)

@router.put("/{user_id}", response_model=Result)
async def update_user(user_id: int, req: UpdateUserInfoRequest,
                        user_service: UserService = Depends(get_user_service)):
    update_num = await user_service.update_user_info(user_id, req)
    if update_num == 0:
        return Result.failure(msg=BizMsg.USER_NOT_FOUND, code=status.HTTP_200_OK)
    return Result.success()

@router.post("/avatar", response_model=Result, description="用户上传头像")
async def upload_avatar(file: UploadFile = File(...), user_service: UserService = Depends(get_user_service)):
    # 新增用户上传的头像
    avatar_url, err_msg = upload_image_to_qiniu(file, f"avatar")
    if avatar_url is None:
        return Result.failure(msg=err_msg, code=status.HTTP_400_BAD_REQUEST)
    # 直接返回url
    return Result.success({"avatar_url": avatar_url})
