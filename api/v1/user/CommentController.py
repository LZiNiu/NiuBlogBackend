from fastapi import APIRouter, Depends, Query, status

from model import Result
from model.dto.comment import CommentCreateDTO
from services.comment import CommentService, get_comment_service
from utils.auth_utils import JwtUtil
from model.common import JwtPayload


router = APIRouter(prefix="/articles/{post_id}/comments", tags=["blog-comments"])


@router.get("")
async def list_comments(post_id: int, page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=50), service: CommentService = Depends(get_comment_service)):
    items, total = await service.list_by_post(post_id, page, size)
    return Result.success({"total": total, "page": page, "size": size, "items": items})


@router.post("")
async def create_comment(post_id: int, dto: CommentCreateDTO, payload: JwtPayload = Depends(JwtUtil.get_payload), service: CommentService = Depends(get_comment_service)):
    cid = await service.create_comment(post_id, dto, int(payload.user_id))
    if not cid:
        return Result.failure(message="评论创建失败", code=status.HTTP_400_BAD_REQUEST)
    return Result.success({"id": cid})
