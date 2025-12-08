from fastapi import APIRouter, Depends

from app.model import Result
from app.services.category import CategoryService, get_category_service


router = APIRouter(prefix="/category", tags=["博客分类"])


@router.get("")
async def list_categories(service: CategoryService = Depends(get_category_service)):
    items = await service.list_all()
    return Result.success(items)


@router.get("/card")
async def list_category_cards(service: CategoryService = Depends(get_category_service)):
    items = await service.list_cards()
    return Result.success(items)