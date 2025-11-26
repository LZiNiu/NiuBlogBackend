from fastapi import APIRouter, Depends, Query, status, UploadFile, File
from pathlib import Path

from model import Result
from starlette.responses import FileResponse
from model.common import PaginatedResponse
from model.dto.post import PostCreateDTO, PostUpdateDTO
from model.vo.post import PostEditVO, PostTableVO
from services.post import PostService, get_post_service
from utils.upload import save_blog
from core.config import settings


from utils.auth_utils import JwtUtil
router = APIRouter(prefix="/articles", tags=["admin-articles"])


@router.get("/pagination", response_model=Result[PaginatedResponse[PostTableVO]])
async def paginated_article_table_info(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=50), category_id: int | None = None, tag_id: int | None = None, service: PostService = Depends(get_post_service)):
    items, total = await service.paginated_table_post_vo(page, size)
    return Result.success(PaginatedResponse(records=items, total=total, current=page, size=size))


@router.get("/{post_id}/editinfo", response_model=Result[PostEditVO])
async def get_article_edit_info(post_id: int, service: PostService = Depends(get_post_service)):
    data = await service.get_article_edit(post_id)
    if not data:
        return Result.failure(message="文章不存在", code=status.HTTP_404_NOT_FOUND)
    return Result.success(data)


@router.post("")
async def create_article(dto: PostCreateDTO, service: PostService = Depends(get_post_service)):
    post_id = await service.create_post(dto)
    return Result.success({"id": post_id})


@router.put("/{post_id}")
async def update_article(post_id: int, dto: PostUpdateDTO, service: PostService = Depends(get_post_service)):
    await service.update_post(post_id, dto)
    return Result.success()


@router.delete("/{post_id}")
async def delete_article(post_id: int, service: PostService = Depends(get_post_service)):
    await service.delete_post(post_id)
    return Result.success()

@router.delete("/batch")
async def delete_articles(ids: list[int], service: PostService = Depends(get_post_service)):
    count = await service.delete_posts(ids)
    return Result.success({"count": count})


@router.put("/{post_id}/status")
async def update_article_status(post_id: int, status_value: str, service: PostService = Depends(get_post_service)):
    ok = await service.update_status(post_id, status_value)
    if not ok:
        return Result.failure(message="状态更新失败", code=status.HTTP_400_BAD_REQUEST)
    return Result.success()


@router.get("/{post_id}/body")
async def get_article_body(post_id: int, service: PostService = Depends(get_post_service)):
    body = await service.get_content(post_id)
    if not body:
        return Result.failure(message="文章不存在或内容缺失", code=status.HTTP_404_NOT_FOUND)
    return FileResponse(body["path"], media_type=body["mime"], filename=Path(body["path"]).name)


@router.post("/upload/blog")
async def upload_blog(file: UploadFile = File(...)):
    content = await file.read()
    _, rel = save_blog(content, file.filename or "post.md")
    return Result.success({"content_file_path": rel})

