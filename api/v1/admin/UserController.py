import time
from fastapi import APIRouter, Depends, Header, HTTPException, Query

from core.config import settings
from model.common import Result
from model.dto.user import AdminCreateUserRequest
from model.common import PagedVO
from services import UserService, get_user_service
from utils.auth_utils import JwtUtil

# admin路由添加鉴权拦截
router = APIRouter(prefix="/users", tags=["admin-users"], dependencies=[Depends(JwtUtil.require_admin)])

@router.get("", response_model=Result[PagedVO])
async def paginate_users_info(current: int = Query(1, ge=1), size: int = Query(10, ge=1, le=10), 
            user_service: UserService = Depends(get_user_service)):
    # 管理员分页查询所有用户信息
    start = time.perf_counter()
    items, total = await user_service.paginate_users_vo(current, size)
    end = time.perf_counter()
    user_service.logger.info(f"管理员分页查询所有用户信息耗时: {end - start:.6f} 秒")
    return Result.success({"total": total, "current": current, "size": size, "records": items})

@router.get("/{user_id}", response_model=Result)
async def get_user_by_id(user_id: int, user_service: UserService = Depends(get_user_service)):
    data = await user_service.get_user_by_id(user_id)
    return Result.success(data)

@router.put("/{user_id}/status", response_model=Result)
async def update_status(user_id: int, status: bool, 
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
