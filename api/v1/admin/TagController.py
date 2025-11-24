from fastapi import APIRouter, Depends, Query

from model import Result, PagedVO
from model.vo.tag import TagVO
from services.tag import TagService, get_tag_service
from model.orm.models import Tag
from model.dto.tag import TagDTO


router = APIRouter(prefix="/tags", tags=["admin-tags"]) 


@router.get("", response_model=Result[list[TagVO]])
async def list_tags(service: TagService = Depends(get_tag_service)):
    items = await service.list_all()
    return Result.success(items)


@router.get("/pagination", response_model=Result[PagedVO])
async def paginated_tags(current: int = Query(ge=1), size: int = Query(ge=1, le=10),
                          service: TagService = Depends(get_tag_service)):
    items, total = await service.paginated_tags(current, size)
    return Result.success(PagedVO(total=total, records=items, current=current, size=size))

@router.post("")
async def create_tag(body: TagDTO, service: TagService = Depends(get_tag_service)):
    name = str(body.name or "").strip()
    obj = Tag(name=name)
    created = await service.mapper.create(service.session, obj)
    return Result.success({"id": created.id})

# @router.post("/batch")
# async def create_tags(tag_names: list[str], service: TagService = Depends(get_tag_service)):
#     await service.create_batch(tag_names)
#     return Result.success()

@router.put("/{tag_id}")
async def update_tag(tag_id: int, body: TagDTO, service: TagService = Depends(get_tag_service)):
    name = str(body.name or "").strip()
    await service.mapper.update(service.session, tag_id, {"name": name})
    return Result.success()


@router.delete("/{tag_id}")
async def delete_tag(tag_id: int, service: TagService = Depends(get_tag_service)):
    ok = await service.mapper.delete(service.session, tag_id)
    if not ok:
        return Result.failure(message="删除失败")
    return Result.success()

@router.delete("/{tag_name}")
async def delete_tag_by_name(tag_name: str, service: TagService = Depends(get_tag_service)):
    ok = await service.mapper.delete_by_filters(service.session, name=tag_name)
    if not ok:
        return Result.failure(message="删除失败, 标签不存在")
    return Result.success()
