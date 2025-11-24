from fastapi import APIRouter, Depends, Query
from model import Result, PagedVO
from model.dto.category import CategoryDTO
from model.vo.category import CategoryVO
from services.category import CategoryService, get_category_service
from model.orm.models import Category
from model.entity.category import Category as pydanticCategory


router = APIRouter(prefix="/categories", tags=["管理端分类管理"])


@router.get("/pagination", response_model=Result[PagedVO])
async def paginated_categories(current: int = Query(ge=1), size: int = Query(ge=1, le=10),
                          service: CategoryService = Depends(get_category_service)):
    items, total = await service.paginated_categories(current, size)
    return Result.success(PagedVO(total=total, records=items, current=current, size=size))

@router.get("", response_model=Result[list[CategoryVO]])
async def list_all_category(service: CategoryService = Depends(get_category_service)):
    items = await service.mapper.list_all(service.session)
    records = list(map(lambda item: CategoryVO(**item), items))
    return Result.success(records)

@router.post("", response_model=Result[pydanticCategory])
async def create_category(category_dto: CategoryDTO, service: CategoryService = Depends(get_category_service)):
    obj = Category(**category_dto.model_dump())
    obj = await service.mapper.create(service.session, obj)
    return Result.success(obj.__dict__)


@router.put("/{category_id}")
async def update_category(category_id: int, category_dto: CategoryDTO, service: CategoryService = Depends(get_category_service)):
    await service.mapper.update(service.session, category_id, category_dto.model_dump())
    return Result.success()


@router.delete("/{category_id}")
async def delete_category(category_id: int, service: CategoryService = Depends(get_category_service)):
    ok = await service.mapper.delete(service.session, category_id)
    if not ok:
        return Result.failure(msg="删除失败")
    return Result.success()
