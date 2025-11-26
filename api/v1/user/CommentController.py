# from fastapi import APIRouter, Depends, Query, status

# from model import Result
# from model.dto.comment import CommentCreateDTO
# from services.comment import CommentService, get_comment_service
# from core.biz_constants import BizCode, BizMsg
# from utils.user_context import get_user_context


# router = APIRouter(prefix="/articles/{post_id}/comments", tags=["blog-comments"])


# @router.get("")
# async def list_comments(post_id: int, page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=50), service: CommentService = Depends(get_comment_service)):
#     items, total = await service.list_by_post(post_id, page, size)
#     return Result.success({"total": total, "page": page, "size": size, "items": items})


# @router.post("")
# async def create_comment(post_id: int, dto: CommentCreateDTO, service: CommentService = Depends(get_comment_service)):
#     ctx = get_user_context()
#     if not ctx:
#         return Result.failure(msg=BizMsg.TOKEN_REQUIRED, code=BizCode.TOKEN_REQUIRED)
#     cid = await service.create_comment(post_id, dto, int(ctx.user_id))
#     if not cid:
#         return Result.failure(message="评论创建失败", code=status.HTTP_400_BAD_REQUEST)
#     return Result.success({"id": cid})
