from fastapi import APIRouter, Depends

from model import Result
from services.category import CategoryService, get_category_service


router = APIRouter(prefix="/categories", tags=["user-categories"])


@router.get("")
async def list_categories(service: CategoryService = Depends(get_category_service)):
    items = await service.list_all()
    return Result.success(items)
