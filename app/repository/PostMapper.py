from typing import Iterable, List, Optional, Tuple

from sqlalchemy import RowMapping, delete, insert, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.vo.post import PostCardVO, PostInfoWithPath, PostTableVO, U_PostInfo
from app.model.orm.models import Category, Post, PostCategory, PostTag, Tag
from app.repository.BaseMapper import BaseMapper


class PostMapper(BaseMapper[Post]):
    def __init__(self):
        super().__init__(Post)

    async def paginate_cards(
        self,
        session: AsyncSession,
        current: int,
        size: int,
        category_id: Optional[int] = None,
        tag_id: Optional[int] = None,
    ) -> Tuple[List[dict], int]:
        
        stmt = (select(*self.select_fields(Post, PostCardVO),
                        func.aggregate_strings(Tag.name.distinct(), ",").label("tag_names"),
                        func.aggregate_strings(Category.name.distinct(), ",").label("category_names"),
                        func.aggregate_strings(PostTag.tag_id.distinct(), ",").label("tag_ids"),
                        func.aggregate_strings(PostCategory.category_id.distinct(), ",").label("category_ids")
                ).select_from(Post)
                .join(PostCategory, PostCategory.post_id == Post.id, isouter=True)
                .join(Category, Category.id == PostCategory.category_id, isouter=True)
                .join(PostTag, PostTag.post_id == Post.id, isouter=True)
                .join(Tag, Tag.id == PostTag.tag_id, isouter=True)
                .group_by(Post.id)
                .order_by(Post.create_time.desc())
                .offset((current - 1) * size)
                .limit(size)
            )
        if category_id is not None:
            stmt = stmt.where(Category.id == category_id)
            total_stmt = select(func.count(PostCategory.post_id)).select_from(PostCategory).where(PostCategory.category_id == category_id)
        else:
            total_stmt = select(func.count()).select_from(Post)
        total = int((await session.execute(total_stmt)).scalar() or 0)
        rows = (await session.execute(stmt)).mappings().all()
        return [dict(r) for r in rows], total
    
    async def get_content_path(self, session: AsyncSession, post_id: int) -> Optional[str]:
        stmt = select(Post.content_file_path).where(Post.id == post_id)
        row: RowMapping = (await session.execute(stmt)).mappings().one_or_none()
        if not row:
            return None
        return row["content_file_path"]

    async def get_post_info_with_path(self, session: AsyncSession, post_id: int) -> PostInfoWithPath | None:
        stmt = (select(*self.select_fields(Post, PostInfoWithPath),
                func.aggregate_strings(Tag.name.distinct(), ",").label("tag_names"),
                func.aggregate_strings(Category.name.distinct(), ",").label("category_names"),
                func.aggregate_strings(PostTag.tag_id.distinct(), ",").label("tag_ids"),
                func.aggregate_strings(PostCategory.category_id.distinct(), ",").label("category_ids"),
            )
            .select_from(Post)
            .join(PostCategory, PostCategory.post_id == Post.id, isouter=True)
            .join(Category, Category.id == PostCategory.category_id, isouter=True)
            .join(PostTag, PostTag.post_id == Post.id, isouter=True)
            .join(Tag, Tag.id == PostTag.tag_id, isouter=True)
            .where(Post.id == post_id)
            .group_by(Post.id)
            .order_by(Post.create_time.desc())
        )
        row: RowMapping = (await session.execute(stmt)).mappings().one()
        if not row:
            return None
        return PostInfoWithPath(**dict(row))
    
    async def get_u_post_info(self, session: AsyncSession, post_id: int) -> U_PostInfo | None:
        """获取用户端文章详情页的文章基本信息
        """
        stmt = (select(*self.select_fields(Post, U_PostInfo),
            func.aggregate_strings(Tag.name.distinct(), ",").label("tag_names"),
            func.aggregate_strings(Category.name.distinct(), ",").label("category_names"),
            func.aggregate_strings(PostTag.tag_id.distinct(), ",").label("tag_ids"),
            func.aggregate_strings(PostCategory.category_id.distinct(), ",").label("category_ids"),
        )
        .select_from(Post)
        .join(PostCategory, PostCategory.post_id == Post.id, isouter=True)
        .join(Category, Category.id == PostCategory.category_id, isouter=True)
        .join(PostTag, PostTag.post_id == Post.id, isouter=True)
        .join(Tag, Tag.id == PostTag.tag_id, isouter=True)
        .where(Post.id == post_id)
        .group_by(Post.id)
        .order_by(Post.create_time.desc())
        )
        row: RowMapping = (await session.execute(stmt)).mappings().one_or_none()
        if not row:
            return None
        return U_PostInfo(**dict(row))

    async def paginated_table_post_vo(self, session: AsyncSession, current: int, size: int) -> list[PostTableVO] | None:
        """获取文章表格展示信息VO, 包含分类、标签等关联信息, 不包含文章内容, """
        # 获取 Post 表的所有列
        colmuns = self.select_fields(Post, PostTableVO)
        stmt = (select(*colmuns,
            func.aggregate_strings(Tag.name.distinct(), ",").label("tag_names"),
            func.aggregate_strings(Category.name.distinct(), ",").label("category_names"),
            func.aggregate_strings(PostTag.tag_id.distinct(), ",").label("tag_ids"),
            func.aggregate_strings(PostCategory.category_id.distinct(), ",").label("category_ids"),
        )
        .select_from(Post)
        .join(PostCategory, PostCategory.post_id == Post.id, isouter=True)
        .join(Category, Category.id == PostCategory.category_id, isouter=True)
        .join(PostTag, PostTag.post_id == Post.id, isouter=True)
        .join(Tag, Tag.id == PostTag.tag_id, isouter=True)
        .group_by(Post.id)
        .order_by(Post.create_time.desc())
        .offset((current - 1) * size)
        .limit(size)
        )
        total = int((await session.execute(select(func.count()).select_from(Post))).scalar() or 0)
        # print("生成的sql: \n", stmt)
        rows: list[RowMapping] = (await session.execute(stmt)).mappings().all()
        if not rows:
            return None
        return [PostTableVO(**dict(r)) for r in rows], total

    async def get_categories(self, session: AsyncSession, post_id: int) -> List[Category]:
        stmt = select(Category).where(Category.id.in_(select(PostCategory.category_id).where(PostCategory.post_id == post_id)))
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_tags(self, session: AsyncSession, post_id: int) -> List[Tag]:
        stmt = select(Tag).where(Tag.id.in_(select(PostTag.tag_id).where(PostTag.post_id == post_id)))
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def add_categories(self, session: AsyncSession, post_id: int, category_ids: Iterable[int]) -> None:
        """为文章新增分类关联：幂等插入，不负责删除。"""
        if category_ids:
            await session.execute(insert(PostCategory).values([{"post_id": post_id, "category_id": cid} for cid in category_ids]))
            await session.commit()

    async def remove_categories(self, session: AsyncSession, post_id: int) -> None:
        """删除文章的所有分类关联。"""
        await session.execute(delete(PostCategory).where(PostCategory.post_id == post_id))
        await session.commit()

    async def add_tags(self, session: AsyncSession, post_id: int, tag_ids: Iterable[int]) -> None:
        """为文章新增标签关联：幂等插入，不负责删除。"""
        if tag_ids:
            await session.execute(insert(PostTag).values([{"post_id": post_id, "tag_id": tid} for tid in tag_ids]))
            await session.commit()

    async def remove_tags(self, session: AsyncSession, post_id: int) -> None:
        """删除文章的所有标签关联。"""
        await session.execute(delete(PostTag).where(PostTag.post_id == post_id))
        await session.commit()

    async def remove_categories_batch(self, session: AsyncSession, post_ids: Iterable[int]) -> None:
        """批量删除文章的所有分类关联。"""
        await session.execute(delete(PostCategory).where(PostCategory.post_id.in_(post_ids)))
        await session.commit()
    
    async def remove_tags_batch(self, session: AsyncSession, post_ids: Iterable[int]) -> None:
        """批量删除文章的所有标签关联。"""
        await session.execute(delete(PostTag).where(PostTag.post_id.in_(post_ids)))
        await session.commit()