from fastapi import APIRouter, Depends

from model import Result
from services.category import CategoryService, get_category_service
from utils.auth_utils import require_admin
from model.entity.models import Category


router = APIRouter(prefix="/admin/categories", tags=["admin-categories"])


@router.get("", dependencies=[Depends(require_admin)])
async def list_categories(service: CategoryService = Depends(get_category_service)):
    items = await service.list_all()
    return Result.success(items)


@router.post("", dependencies=[Depends(require_admin)])
async def create_category(body: dict, service: CategoryService = Depends(get_category_service)):
    name = str(body.get("name") or "").strip()
    description = body.get("description")
    obj = Category(name=name, description=description)
    created = await service.mapper.create(service.session, obj)
    return Result.success({"id": created.id})


@router.put("/{category_id}", dependencies=[Depends(require_admin)])
async def update_category(category_id: int, body: dict, service: CategoryService = Depends(get_category_service)):
    await service.mapper.update(service.session, category_id, body)
    return Result.success()


@router.delete("/{category_id}", dependencies=[Depends(require_admin)])
async def delete_category(category_id: int, service: CategoryService = Depends(get_category_service)):
    ok = await service.mapper.delete(service.session, category_id)
    if not ok:
        return Result.failure(message="删除失败")
    return Result.success()
