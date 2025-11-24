from fastapi import APIRouter, Depends, Query, status
from pathlib import Path

from model import Result, PagedVO
from model.vo.post import PostCardVO, UserendPostDetailVO, PostMeta, PostTableVO
from starlette.responses import FileResponse
from services.post import PostService, get_post_service


router = APIRouter(prefix="/articles", tags=["blog-articles"])


@router.get("", response_model=Result[PagedVO])
async def list_article_cards(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=50), 
                                category_id: int | None = None, tag_id: int | None = None, 
                                service: PostService = Depends(get_post_service)):
    data = await service.list_cards(page, size, category_id, tag_id)
    return Result.success(data)


@router.get("/{post_id}", response_model=Result[UserendPostDetailVO])
async def get_article_detail(post_id: int, service: PostService = Depends(get_post_service)):
    data = await service.get_article_complete(post_id)
    if not data:
        return Result.failure(message="文章不存在", code=status.HTTP_404_NOT_FOUND)
    return Result.success(data)


@router.get("/{post_id}/meta", response_model=Result[PostMeta])
async def get_article_meta(post_id: int, service: PostService = Depends(get_post_service)):
    data = await service.get_article_meta(post_id)
    if not data:
        return Result.failure(message="文章不存在或内容缺失", code=status.HTTP_404_NOT_FOUND)
    return Result.success(data)


@router.get("/{post_id}/body")
async def get_article_body(post_id: int, service: PostService = Depends(get_post_service)):
    body_text = await service.get_content(post_id)
    if not body_text:
        return Result.failure(message="文章不存在或内容缺失", code=status.HTTP_404_NOT_FOUND)
    return Result.success(body_text)


@router.get("/{post_id}/likes/count")
async def like_count(post_id: int, service: PostService = Depends(get_post_service)):
    detail = await service.get_article_complete(post_id)
    if not detail:
        return Result.failure(message="文章不存在", code=status.HTTP_404_NOT_FOUND)
    return Result.success({"count": detail.get("like_count", 0)})


@router.post("/{post_id}/likes")
async def like(post_id: int, service: PostService = Depends(get_post_service)):
    ok = await service.increment_like_count(post_id)
    if not ok:
        return Result.failure(message="点赞失败", code=status.HTTP_404_NOT_FOUND)
    return Result.success()
