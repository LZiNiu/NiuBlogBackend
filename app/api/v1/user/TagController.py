from fastapi import APIRouter, Depends

from app.model import Result
from app.services.tag import TagService, get_tag_service


router = APIRouter(prefix="/tags", tags=["用户端标签接口"])


@router.get("")
async def list_tags(service: TagService = Depends(get_tag_service)):
    items = await service.list_all()
    return Result.success(items)
