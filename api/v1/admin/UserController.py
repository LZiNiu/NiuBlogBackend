from fastapi import APIRouter, HTTPException, Depends
from fastapi import Header, Query
from model import Result
from model.common import JwtPayload
from services import get_user_service, UserService
from model.user import UpdateUserStatusRequest, AdminCreateUserRequest, UserLoginRequest
from utils.auth_utils import get_payload
from core.config import settings

admin_router = APIRouter(prefix="/admin/users", tags=["admin-users"])

def _require_admin(payload: JwtPayload) -> tuple[int, bool]:
    user_id = int(payload.user_id)  # type: ignore
    role = payload.role
    is_super = user_id == settings.SUPER_ADMIN_USER_ID
    if role != "admin" and not is_super:
        raise HTTPException(status_code=403, detail="Forbidden")
    return user_id, is_super

@admin_router.get("", response_model=Result)
def list_users(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=10), 
            authorization: str = Header(...), 
            user_service: UserService = Depends(get_user_service)):
    payload = get_payload(authorization)
    items, total = user_service.list_users(payload, page, size)
    return Result.success({"total": total, "page": page, "size": size, "items": items})

@admin_router.get("/{user_id}", response_model=Result)
def get_user_by_id(user_id: int, authorization: str = Header(...), user_service: UserService = Depends(get_user_service)):
    payload = get_payload(authorization)
    data = user_service.get_user_by_id(payload, user_id)
    return Result.success(data)

@admin_router.put("/{user_id}/status", response_model=Result)
def update_status(user_id: int, req: UpdateUserStatusRequest, 
                        authorization: str = Header(...), 
                        user_service: UserService = Depends(get_user_service)):
    payload = get_payload(authorization)
    actor_id, _ = _require_admin(payload)
    data = user_service.update_user_status(actor_id, user_id, req)
    return Result.success(data)

@admin_router.delete("/{user_id}", response_model=Result)
def delete_user(user_id: int, authorization: str = Header(...), user_service: UserService = Depends(get_user_service)):
    payload = get_payload(authorization)
    actor_id, _ = _require_admin(payload)
    user_service.delete_user(actor_id, user_id)
    return Result.success()

@admin_router.post("", response_model=Result)
def create_user(req: AdminCreateUserRequest, authorization: str = Header(...), user_service: UserService = Depends(get_user_service)):
    payload = get_payload(authorization)
    actor_id, _ = _require_admin(payload)
    data = user_service.admin_create_user(actor_id, req)
    return Result.success(data)
