from typing import List, Optional, Tuple
from pathlib import Path
import aiofiles
import mimetypes
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from model.common import PagedVO
from repository.CategoryMapper import CategoryMapper
from repository.PostMapper import PostMapper
from repository.TagMapper import TagMapper
from model.enums import PostStatus
from model.db import get_session
from model.dto.post import PostCreateDTO, PostUpdateDTO
from model.orm.models import Post
from model.vo.post import PostCardVO, UserendPostDetailVO, PostBodyMeta, PostEditVO, PostMeta, PostTableVO
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

    async def list_cards(self, page: int, size: int, category_id: Optional[int] = None, tag_id: Optional[int] = None) -> PagedVO:
        rows, total = await self.post_mapper.paginate_cards(self.session, page, size, category_id, tag_id)
        return PagedVO(total=total, records=rows, current=page, size=size)

    async def paginated_table_post_vo(self, page: int, size: int) -> Tuple[list[PostTableVO], int] | None:
        row, total = await self.post_mapper.paginated_table_post_vo(self.session, page, size)
        if not row:
            return None, 0
        return row, total

    async def get_article_meta(self, post_id: int) -> PostMeta | None:
        row = await self.post_mapper.get_post_meta(self.session, post_id)
        if not row:
            return None
        return PostMeta(**row.model_dump())

    async def get_article_edit(self, post_id: int)->PostEditVO:
        row = await self.post_mapper.get_post_info_with_path(self.session, post_id)
        if not row:
            return None
        # 获取文章正文
        path = Path(row.content_file_path)
        if not path.is_absolute():
            path = settings.app.BLOG_STORAGE_DIR / path
        try:
            async with aiofiles.open(str(path), "r", encoding="utf-8") as f:
                content = await f.read()
        except Exception as e:
            self.logger.error(f"读取文章正文文件失败: {e}")
            content = ""
        return PostEditVO(**row.model_dump(), content=content)

    async def get_article_complete(self, post_id: int) -> UserendPostDetailVO | None:
        row = await self.post_mapper.get_post_info_with_path(self.session, post_id)
        if not row:
            return None
        try:
            path = Path(row.content_file_path)
            if not path.is_absolute():
                path = settings.app.BLOG_STORAGE_DIR / path
            if path.is_file():
                async with aiofiles.open(str(path), "r", encoding="utf-8") as f:
                    content = await f.read()
        except Exception as e:
            self.logger.error(f"读取文章正文文件失败: {e}")
            content = ""
        return UserendPostDetailVO(**row.model_dump(), content=content)

    async def create_post(self, dto: PostCreateDTO) -> int:
        # 保存文章正文文件
        if dto.content is not None:
            content_file_path = settings.app.BLOG_STORAGE_DIR / f"{dto.title}.md"
            async with aiofiles.open(str(content_file_path), "w", encoding="utf-8") as f:
                await f.write(dto.content)
        else:
            content_file_path = None
        # 保存元信息
        obj = Post(
            title=dto.title,
            summary=dto.summary,
            content_file_path=content_file_path,
            status=dto.post_status or PostStatus.DRAFT,
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
        # 分离content
        content = update_dict.pop("content", None)
        self.logger.debug(f"更新文章{post_id}")
        await self.post_mapper.update(self.session, post_id, update_dict)
        self.logger.debug(f"post: {post_id}: 删除关联表信息")
        await self.post_mapper.remove_categories(self.session, post_id)
        await self.post_mapper.remove_tags(self.session, post_id)
        if rel_categories is not None:
            await self.post_mapper.add_categories(self.session, post_id, rel_categories or [])
        if rel_tags is not None:
            await self.post_mapper.add_tags(self.session, post_id, rel_tags or [])
        # 更新内容
        self.logger.debug(f"post: {post_id}: 关联表更新完成")
        # 1. 查出路径
        content_file_path = await self.post_mapper.get_content_path(self.session, post_id)
        if not content_file_path:
            return
        # 2. 写入内容
        path = Path(content_file_path)
        if not path.is_absolute():
            path = settings.app.BLOG_STORAGE_DIR / path
        self.logger.debug(f"post: {post_id}: 尝试打开内容文件路径: {path}")
        async with aiofiles.open(str(path), "w", encoding="utf-8") as f:
            self.logger.debug(f"post: {post_id}: 尝试保存内容")
            await f.write(content)

    async def delete_post(self, post_id: int) -> None:
        await self.post_mapper.delete(self.session, post_id)

    async def update_status(self, post_id: int, status_value: str) -> bool:
        await self.post_mapper.update(self.session, post_id, {"status": status_value})
        return True

    async def get_content(self, post_id: int) -> str | None:
        path = await self.post_mapper.get_content_path(self.session, post_id)
        if not path:
            return None
        try:
            path = Path(path)
            if not path.is_absolute():
                path = settings.app.BLOG_STORAGE_DIR / path
            if not path.is_file():
                self.logger.info(f"文件不存在: {path}")
                return None
            async with aiofiles.open(str(path), "r", encoding="utf-8") as f:
                content = await f.read()
                return content
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
