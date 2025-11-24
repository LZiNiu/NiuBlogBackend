from fastapi import APIRouter, Depends, Query

from model import Result
from services.comment import CommentService, get_comment_service
from model.entity.models import Comment


router = APIRouter(prefix="/admin/comments", tags=["admin-comments"]) 


@router.get("")
async def list_comments(post_id: int | None = None, status: str | None = None, page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=50), service: CommentService = Depends(get_comment_service)):
    if post_id is not None:
        items, total = await service.mapper.list_by_post(service.session, post_id, page, size)
        return Result.success({"total": total, "page": page, "size": size, "items": items})
    filters = {}
    if status:
        filters["status"] = status
    data = await service.mapper.get_all(service.session, filters=filters, order_by=["-created_at"], limit=size, offset=(page - 1) * size)
    total = await service.mapper.count(service.session, **filters)
    return Result.success({"total": total, "page": page, "size": size, "items": [i.__dict__ for i in data]})


@router.put("/{comment_id}/status")
async def update_comment_status(comment_id: int, status_value: str, service: CommentService = Depends(get_comment_service)):
    obj = await service.mapper.update(service.session, comment_id, {"status": status_value})
    if not obj:
        return Result.failure(message="更新失败")
    return Result.success()


@router.delete("/{comment_id}")
async def delete_comment(comment_id: int, service: CommentService = Depends(get_comment_service)):
    ok = await service.mapper.delete(service.session, comment_id)
    if not ok:
        return Result.failure(message="删除失败")
    return Result.success()
