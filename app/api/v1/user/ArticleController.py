from fastapi import APIRouter, Depends, Query, status

from app.model import Result
from app.model.common import PaginatedResponse
from app.model.vo.post import PostCardVO, U_PostInfo
from app.services.post import PostService, get_post_service


router = APIRouter(prefix="/articles", tags=["用户端文章接口"])


@router.get("/pagination", response_model=Result[PaginatedResponse[PostCardVO]])
async def paginated_article_cards(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=50), 
                                    category_id: int | None = None, tag_id: int | None = None, 
                                    service: PostService = Depends(get_post_service)):
    pagevo = await service.paginated_card_info(page, size, category_id, tag_id)
    return Result.success(pagevo)


@router.get("/{post_id}/body", response_model=Result[str])
async def get_article_body(post_id: int, service: PostService = Depends(get_post_service)):
    body_text = await service.get_content(post_id)
    if not body_text:
        return Result.failure(message="文章不存在或内容缺失", code=status.HTTP_404_NOT_FOUND)
    return Result.success(body_text)

@router.get("/{post_id}/info", response_model=Result[U_PostInfo])
async def get_article_info_by_id(post_id: int, service: PostService = Depends(get_post_service)):
    data = await service.get_u_post_info(post_id)
    if not data:
        return Result.failure(message="文章不存在", code=status.HTTP_404_NOT_FOUND)
    return Result.success(data)


@router.get("/category/{category_id}", response_model=Result[PaginatedResponse[PostCardVO]])
async def list_articles_by_category(category_id: int, page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=15), 
                                    service: PostService = Depends(get_post_service)):
    items = await service.paginated_card_info(page, size, category_id=category_id)
    return Result.success(items)

@router.post("/{post_id}/likes")
async def like(post_id: int, service: PostService = Depends(get_post_service)):
    ok = await service.increment_like_count(post_id)
    if not ok:
        return Result.failure(message="点赞失败", code=status.HTTP_404_NOT_FOUND)
    return Result.success()
