from fastapi import APIRouter, Depends, Header, HTTPException, Query

from core.config import settings
from model.common import Result
from model.dto.user import AdminCreateUserRequest
from services import UserService, get_user_service
from utils.auth_utils import require_admin

# admin路由添加鉴权拦截
admin_router = APIRouter(prefix="/admin/users", tags=["admin-users"], dependencies=[Depends(require_admin)])

@admin_router.get("", response_model=Result)
async def paginate_users_info(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=10), 
            user_service: UserService = Depends(get_user_service)):
    # 管理员分页查询所有用户信息
    items, total = await user_service.paginate_users_vo(page, size)
    return Result.success({"total": total, "page": page, "size": size, "items": items})

@admin_router.get("/{user_id}", response_model=Result)
async def get_user_by_id(user_id: int, user_service: UserService = Depends(get_user_service)):
    data = await user_service.get_user_by_id(user_id)
    return Result.success(data)

@admin_router.put("/{user_id}/status", response_model=Result)
async def update_status(user_id: int, status: bool, 
                        user_service: UserService = Depends(get_user_service)):
    data = await user_service.update_user_status(user_id, status)
    return Result.success(data)

@admin_router.delete("/{user_id}", response_model=Result)
async def delete_user(user_id: int, 
                        user_service: UserService = Depends(get_user_service)):
    # 不允许删除超级管理员
    if user_id == settings.SUPER_ADMIN_USER_ID:
        raise HTTPException(status_code=403, detail="无权删除超级管理员")
    await user_service.delete_user(user_id)
    return Result.success()

@admin_router.post("", response_model=Result)
async def create_user(req: AdminCreateUserRequest, user_service: UserService = Depends(get_user_service)):
    data = await user_service.admin_create_user(req)
    return Result.success(data)
