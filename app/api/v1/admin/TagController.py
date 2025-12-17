from datetime import datetime, timezone
from fastapi import APIRouter, Depends

from app.core.biz_constants import BizMsg
from app.model import Result
from app.model.common import PaginatedResponse
from app.model.dto.common import BatchDelete
from app.model.dto.tag import TagCreate, TagUpdate
from app.model.vo.common import CreateResponse
from app.services.tag import TagService, get_tag_service
from app.model.entity import Tag


router = APIRouter(prefix="/tags", tags=["管理端标签接口"]) 


@router.get("")
async def list_tags(service: TagService = Depends(get_tag_service)):
    items = await service.list_all()
    return Result.success(items)

@router.get("/pagination", response_model=Result[PaginatedResponse[Tag]])
async def paginated_tags(page: int = 1, size: int = 10, service: TagService = Depends(get_tag_service)):
    items, total = await service.paginated_tags(page, size)
    return Result.success(PaginatedResponse(records=items, total=total, current=page, size=size))


@router.post("", response_model=Result[CreateResponse])
async def create_tag(tagdto: TagCreate, service: TagService = Depends(get_tag_service)):
    obj_id = await service.mapper.create(service.session, tagdto)
    return Result.success(CreateResponse(id=obj_id))


@router.put("/{tag_id}")
async def update_tag(tag_id: int, tagdto: TagUpdate, service: TagService = Depends(get_tag_service)):
    name = tagdto.name.strip()
    description = tagdto.description.strip() if tagdto.description else None
    await service.mapper.update(service.session, tag_id, {"name": name, "description": description})
    return Result.success()


@router.delete("/{tag_id}")
async def delete_tag(tag_id: int, service: TagService = Depends(get_tag_service)):
    ok = await service.mapper.delete(service.session, tag_id)
    if not ok:
        return Result.failure(BizMsg.DB_RECORD_NOT_FOUND)
    return Result.success()


@router.delete("/batch")
async def delete_tags(batch_delete: BatchDelete, service: TagService = Depends(get_tag_service)):
    ok = await service.mapper.delete_batch(service.session, batch_delete.ids)
    if not ok:
        return Result.failure(BizMsg.DB_RECORD_NOT_FOUND)
    return Result.success()
