from fastapi import APIRouter, Depends

from app.model import Result
from app.model.common import PaginatedResponse
from app.model.dto.category import CategoryCreate
from app.model.vo.common import CreateResponse
from app.services.category import CategoryService, get_category_service
from app.model.entity import Category


router = APIRouter(prefix="/categories", tags=["管理端分类接口"]) 


@router.get("")
async def list_categories(service: CategoryService = Depends(get_category_service)):
    items = await service.list_all()
    return Result.success(items)
    
@router.get("/pagination", response_model=Result[PaginatedResponse[Category]])
async def paginated_categories(page: int = 1, size: int = 10, service: CategoryService = Depends(get_category_service)):
    items, total = await service.paginated_categories(page, size)
    return Result.success(PaginatedResponse(records=items, total=total, current=page, size=size))


@router.post("", response_model=Result[CreateResponse])
async def create_category(body: CategoryCreate, service: CategoryService = Depends(get_category_service)):
    category_id = await service.mapper.create(service.session, body)
    return Result.success(CreateResponse(id=category_id))


@router.put("/{category_id}")
async def update_category(category_id: int, body: dict, service: CategoryService = Depends(get_category_service)):
    await service.mapper.update(service.session, category_id, body)
    return Result.success()


@router.delete("/{category_id}")
async def delete_category(category_id: int, service: CategoryService = Depends(get_category_service)):
    ok = await service.mapper.delete(service.session, category_id)
    if not ok:
        return Result.failure(message="删除失败")
    return Result.success()
