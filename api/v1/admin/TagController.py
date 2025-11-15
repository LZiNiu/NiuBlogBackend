from fastapi import APIRouter, Depends

from model import Result
from services.tag import TagService, get_tag_service
from utils.auth_utils import require_admin
from model.entity.models import Tag


router = APIRouter(prefix="/admin/tags", tags=["admin-tags"])


@router.get("", dependencies=[Depends(require_admin)])
async def list_tags(service: TagService = Depends(get_tag_service)):
    items = await service.list_all()
    return Result.success(items)


@router.post("", dependencies=[Depends(require_admin)])
async def create_tag(body: dict, service: TagService = Depends(get_tag_service)):
    name = str(body.get("name") or "").strip()
    obj = Tag(name=name)
    created = await service.mapper.create(service.session, obj)
    return Result.success({"id": created.id})


@router.put("/{tag_id}", dependencies=[Depends(require_admin)])
async def update_tag(tag_id: int, body: dict, service: TagService = Depends(get_tag_service)):
    await service.mapper.update(service.session, tag_id, body)
    return Result.success()


@router.delete("/{tag_id}", dependencies=[Depends(require_admin)])
async def delete_tag(tag_id: int, service: TagService = Depends(get_tag_service)):
    ok = await service.mapper.delete(service.session, tag_id)
    if not ok:
        return Result.failure(message="删除失败")
    return Result.success()
