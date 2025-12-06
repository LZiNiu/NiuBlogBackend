from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from handler.exception_handlers import AuthenticationException
from core.config import settings
from model.common import Result
from model.dto.user import AdminCreateUserRequest, UpdateUserStatus
from model.common import PaginatedResponse
from services import UserService, get_user_service
from utils.upload import upload_image_to_qiniu
from utils.user_context import get_user_context
from core.biz_constants import BizCode, BizMsg

# admin路由添加鉴权拦截
router = APIRouter(prefix="/users", tags=["admin-users"])

@router.get("/pagination", response_model=Result[PaginatedResponse])
async def paginate_users_info(current: int = Query(1, ge=1), size: int = Query(10, ge=1, le=10), 
            user_service: UserService = Depends(get_user_service)):
    # 管理员分页查询所有用户信息
    items, total = await user_service.paginate_users_vo(current, size)
    return Result.success({"total": total, "current": current, "size": size, "records": items})

# 该路由应放在路径参数路由之前, 否则fastapi无法区分, 将报错422
@router.get("/info", response_model=Result)
async def get_user_info(user_service: UserService = Depends(get_user_service)):
    ctx = get_user_context()
    if not ctx:
        return Result.failure(msg=BizMsg.TOKEN_REQUIRED, code=BizCode.TOKEN_REQUIRED)
    user_id = int(ctx.user_id)
    data = await user_service.get_user_info(user_id)
    return Result.success(data)


@router.get("/{user_id}", response_model=Result)
async def get_user_by_id(user_id: int, user_service: UserService = Depends(get_user_service)):
    data = await user_service.get_user_by_id(user_id)
    return Result.success(data)


@router.put("/{user_id}/status", response_model=Result)
async def update_status(user_id: int, status: UpdateUserStatus, 
                        user_service: UserService = Depends(get_user_service)):
    row_count = await user_service.update_user_status(user_id, status)
    if row_count == 0:
        raise AuthenticationException("用户不存在")
    return Result.success({'user_id': user_id})

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


@router.post("/avatar")
def upload_avatar(file: UploadFile = File(...), user_service: UserService = Depends(get_user_service)):
    # 保存文件到指定目录
    avatar_url, reason = upload_image_to_qiniu(file, "avatar")
    if not avatar_url:
        return Result.failure(msg=reason, code=status.HTTP_422_UNPROCESSABLE_CONTENT)
    return Result.success({"avatar_url": avatar_url})