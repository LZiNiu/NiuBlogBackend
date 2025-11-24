from fastapi import APIRouter, Depends

from model import Result
from services.tag import TagService, get_tag_service


router = APIRouter(prefix="/tags", tags=["blog-tags"])


@router.get("")
async def list_tags(service: TagService = Depends(get_tag_service)):
    items = await service.list_all()
    return Result.success(items)
