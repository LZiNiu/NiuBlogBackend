from fastapi import APIRouter, Depends, Query, status, UploadFile, File
from pathlib import Path

from model import Result
from starlette.responses import FileResponse
from model.dto.post import PostCreateDTO, PostUpdateDTO
from model.vo.post import PostDetailVO
from services.post import PostService, get_post_service
from utils.auth_utils import require_admin
from utils.upload import save_blog
from core.config import settings


router = APIRouter(prefix="/admin/articles", tags=["admin-articles"])


@router.get("")
async def list_articles(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=50), category_id: int | None = None, tag_id: int | None = None, service: PostService = Depends(get_post_service)):
    items, total = await service.list_cards(page, size, category_id, tag_id)
    return Result.success({"total": total, "page": page, "size": size, "items": items})


@router.get("/{post_id}", response_model=PostDetailVO)
async def get_article_detail(post_id: int, service: PostService = Depends(get_post_service)):
    data = await service.get_detail(post_id)
    if not data:
        return Result.failure(message="文章不存在", code=status.HTTP_404_NOT_FOUND)
    return Result.success(data)


@router.post("", dependencies=[Depends(require_admin)])
async def create_article(dto: PostCreateDTO, service: PostService = Depends(get_post_service)):
    post_id = await service.create_post(dto)
    return Result.success({"id": post_id})


@router.put("/{post_id}", dependencies=[Depends(require_admin)])
async def update_article(post_id: int, dto: PostUpdateDTO, service: PostService = Depends(get_post_service)):
    await service.update_post(post_id, dto)
    return Result.success()


@router.delete("/{post_id}", dependencies=[Depends(require_admin)])
async def delete_article(post_id: int, service: PostService = Depends(get_post_service)):
    await service.delete_post(post_id)
    return Result.success()


@router.put("/{post_id}/status", dependencies=[Depends(require_admin)])
async def update_article_status(post_id: int, status_value: str, service: PostService = Depends(get_post_service)):
    ok = await service.update_status(post_id, status_value)
    if not ok:
        return Result.failure(message="状态更新失败", code=status.HTTP_400_BAD_REQUEST)
    return Result.success()


@router.get("/{post_id}/body")
async def get_article_body(post_id: int, service: PostService = Depends(get_post_service)):
    body = await service.get_body_meta(post_id)
    if not body:
        return Result.failure(message="文章不存在或内容缺失", code=status.HTTP_404_NOT_FOUND)
    return FileResponse(body["path"], media_type=body["mime"], filename=Path(body["path"]).name)


@router.get("/{post_id}/likes/count")
async def like_count(post_id: int, service: PostService = Depends(get_post_service)):
    detail = await service.get_detail(post_id)
    if not detail:
        return Result.failure(message="文章不存在", code=status.HTTP_404_NOT_FOUND)
    return Result.success({"count": detail.get("like_count", 0)})


@router.post("/{post_id}/likes", dependencies=[Depends(require_admin)])
async def like(post_id: int, service: PostService = Depends(get_post_service)):
    ok = await service.increment_like_count(post_id)
    if not ok:
        return Result.failure(message="点赞失败", code=status.HTTP_404_NOT_FOUND)
    return Result.success()

@router.get("/content/files", dependencies=[Depends(require_admin)])
async def list_blog_files():
    base = settings.BLOG_STORAGE_DIR.resolve()
    items = []
    for p in base.rglob("*.md"):
        rel = p.relative_to(base)
        items.append({"name": p.name, "path": str(rel)})
    return Result.success(items)

@router.post("/upload/blog", dependencies=[Depends(require_admin)])
async def upload_blog(file: UploadFile = File(...)):
    content = await file.read()
    _, rel = save_blog(content, file.filename or "post.md")
    return Result.success({"content_file_path": rel})

@router.put("/{post_id}/content-path", dependencies=[Depends(require_admin)])
async def update_content_path(post_id: int, dto: PostUpdateDTO, service: PostService = Depends(get_post_service)):
    await service.update_post(post_id, PostUpdateDTO(content_file_path=dto.content_file_path))
    return Result.success()
