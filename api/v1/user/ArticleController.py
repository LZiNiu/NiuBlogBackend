from fastapi import APIRouter, Depends, Query, status
from pathlib import Path

from model import Result
from starlette.responses import FileResponse
from services.post import PostService, get_post_service


router = APIRouter(prefix="/articles", tags=["blog-articles"])


@router.get("")
async def list_articles(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=50), category_id: int | None = None, tag_id: int | None = None, service: PostService = Depends(get_post_service)):
    items, total = await service.list_cards(page, size, category_id, tag_id)
    return Result.success({"total": total, "page": page, "size": size, "items": items})


@router.get("/{post_id}")
async def get_article_detail(post_id: int, service: PostService = Depends(get_post_service)):
    data = await service.get_detail(post_id)
    if not data:
        return Result.failure(message="文章不存在", code=status.HTTP_404_NOT_FOUND)
    return Result.success(data)


@router.get("/{post_id}/body")
async def get_article_body(post_id: int, service: PostService = Depends(get_post_service)):
    body = await service.get_body_meta(post_id)
    if not body:
        return Result.failure(message="文章不存在或内容缺失", code=status.HTTP_404_NOT_FOUND)
    return FileResponse(body.path, media_type=body.mime)


@router.get("/{post_id}/likes/count")
async def like_count(post_id: int, service: PostService = Depends(get_post_service)):
    detail = await service.get_detail(post_id)
    if not detail:
        return Result.failure(message="文章不存在", code=status.HTTP_404_NOT_FOUND)
    return Result.success({"count": detail.get("like_count", 0)})


@router.post("/{post_id}/likes")
async def like(post_id: int, service: PostService = Depends(get_post_service)):
    ok = await service.increment_like_count(post_id)
    if not ok:
        return Result.failure(message="点赞失败", code=status.HTTP_404_NOT_FOUND)
    return Result.success()
