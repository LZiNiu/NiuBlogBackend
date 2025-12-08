from datetime import datetime, timezone
from fastapi import APIRouter, Depends

from app.model import Result
from app.model.common import PaginatedResponse
from app.model.dto.tag import TagDTO
from app.services.tag import TagService, get_tag_service
from app.model.entity import Tag


router = APIRouter(prefix="/tags", tags=["admin-tags"]) 


@router.get("")
async def list_tags(service: TagService = Depends(get_tag_service)):
    items = await service.list_all()
    return Result.success(items)

@router.get("/pagination", response_model=Result[PaginatedResponse[Tag]])
async def paginated_tags(page: int = 1, size: int = 10, service: TagService = Depends(get_tag_service)):
    items, total = await service.paginated_tags(page, size)
    return Result.success(PaginatedResponse(records=items, total=total, current=page, size=size))

@router.post("")
async def create_tag(tagdto: TagDTO, service: TagService = Depends(get_tag_service)):
    tag = Tag(**tagdto.model_dump(exclude={"description"}))
    tag.create_time = datetime.now(timezone.utc)
    tag.update_time = datetime.now(timezone.utc)
    obj_id = await service.mapper.create(service.session, tag)
    tag.id = obj_id
    return Result.success(tag)


@router.put("/{tag_id}")
async def update_tag(tag_id: int, tagdto: TagDTO, service: TagService = Depends(get_tag_service)):
    name = tagdto.name.strip()
    description = tagdto.description.strip() if tagdto.description else None
    await service.mapper.update(service.session, tag_id, {"name": name, "description": description})
    return Result.success()


@router.delete("/{tag_id}")
async def delete_tag(tag_id: int, service: TagService = Depends(get_tag_service)):
    ok = await service.mapper.delete(service.session, tag_id)
    if not ok:
        return Result.failure(message="删除失败")
    return Result.success()
