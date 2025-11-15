from typing import Dict, List, Optional, Tuple
from pathlib import Path
import aiofiles
import mimetypes
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from dao.CategoryMapper import CategoryMapper
from dao.PostMapper import PostMapper
from dao.TagMapper import TagMapper
from model.db import get_session
from model.dto.post import PostCreateDTO, PostUpdateDTO
from model.entity.models import Post
from model.vo.post import PostCardVO, PostDetailVO, SimpleCategoryVO, PostBodyMetaVO
from services.base import BaseService


def get_post_mapper() -> PostMapper:
    return PostMapper()


def get_category_mapper() -> CategoryMapper:
    return CategoryMapper()


def get_tag_mapper() -> TagMapper:
    return TagMapper()


class PostService(BaseService):
    def __init__(self, session: AsyncSession, post_mapper: PostMapper, category_mapper: CategoryMapper, tag_mapper: TagMapper):
        super().__init__(session)
        self.post_mapper = post_mapper
        self.category_mapper = category_mapper
        self.tag_mapper = tag_mapper

    async def list_cards(self, page: int, size: int, category_id: Optional[int] = None, tag_id: Optional[int] = None) -> Tuple[List[PostCardVO | dict], int]:
        rows, total = await self.post_mapper.paginate_cards(self.session, page, size, category_id, tag_id)
        return rows, total

    async def get_detail(self, post_id: int) -> PostDetailVO | dict | None:
        row = await self.post_mapper.get_detail(self.session, post_id)
        if not row:
            return None
        try:
            path = Path(row.content_file_path)
            if not path.is_absolute():
                path = settings.app.BLOG_STORAGE_DIR / path
            if path.is_file():
                async with aiofiles.open(str(path), "r", encoding="utf-8") as f:
                    row.body_text = await f.read()
        except Exception as e:
            self.logger.error(f"读取文章正文文件失败: {e}")
            row.body_text = ""
        return row

    async def create_post(self, dto: PostCreateDTO) -> int:
        obj = Post(
            title=dto.title,
            summary=dto.summary,
            content_file_path=dto.content_file_path,
            status=dto.status or "draft",
            author_id=settings.app.AUTHOR_ID,
            author_name=settings.app.AUTHOR_NAME,
        )
        await self.post_mapper.create(self.session, obj)
        await self.post_mapper.remove_categories(self.session, obj.id)
        await self.post_mapper.add_categories(self.session, obj.id, dto.category_ids)
        await self.post_mapper.remove_tags(self.session, obj.id)
        await self.post_mapper.add_tags(self.session, obj.id, dto.tag_ids)
        return obj.id

    async def update_post(self, post_id: int, dto: PostUpdateDTO) -> None:
        update_dict = dto.model_dump(exclude_unset=True)
        rel_categories = update_dict.pop("category_ids", None)
        rel_tags = update_dict.pop("tag_ids", None)
        await self.post_mapper.update(self.session, post_id, update_dict)
        if rel_categories is not None:
            await self.post_mapper.remove_categories(self.session, post_id)
            await self.post_mapper.add_categories(self.session, post_id, rel_categories or [])
        if rel_tags is not None:
            await self.post_mapper.remove_tags(self.session, post_id)
            await self.post_mapper.add_tags(self.session, post_id, rel_tags or [])

    async def delete_post(self, post_id: int) -> None:
        await self.post_mapper.delete(self.session, post_id)

    async def update_status(self, post_id: int, status_value: str) -> bool:
        await self.post_mapper.update(self.session, post_id, {"status": status_value})
        return True

    async def get_body_meta(self, post_id: int) -> PostBodyMetaVO | None:
        data = await self.post_mapper.get_detail(self.session, post_id)
        if not data:
            return None
        try:
            path = Path(data.content_file_path)
            if not path.is_absolute():
                path = settings.app.BLOG_STORAGE_DIR / path
            if not path.is_file():
                self.logger.info(f"文件不存在: {path}")
                return None
            size = path.stat().st_size
            mime, _ = mimetypes.guess_type(str(path))
            return PostBodyMetaVO(path=str(path), size=size, mime=mime or "text/plain")
        except Exception:
            return None

    async def increment_like_count(self, post_id: int) -> bool:
        obj = await self.post_mapper.get_by_id(self.session, post_id)
        if not obj:
            return False
        await self.post_mapper.update(self.session, post_id, {"like_count": obj.like_count + 1})
        return True


def get_post_service(
    session: AsyncSession = Depends(get_session),
    post_mapper: PostMapper = Depends(get_post_mapper),
    category_mapper: CategoryMapper = Depends(get_category_mapper),
    tag_mapper: TagMapper = Depends(get_tag_mapper),
) -> PostService:
    return PostService(session, post_mapper, category_mapper, tag_mapper)
