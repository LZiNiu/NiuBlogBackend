from typing import Iterable, List, Optional, Tuple

from sqlalchemy import RowMapping, delete, insert, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import settings

from model.vo.post import PostDetailVO
from model.orm.models import Category, Post, PostCategory, PostTag, Tag
from dao.BaseMapper import BaseMapper


class PostMapper(BaseMapper[Post]):
    def __init__(self):
        super().__init__(Post)

    def _agg_names_expr(self, alias: str, col: str = "name") -> str:
        url = settings.db.URL.lower()
        if url.startswith("postgres"):
            return f"STRING_AGG({alias}.{col}, ',')"
        if url.startswith("mysql"):
            return f"GROUP_CONCAT({alias}.{col} SEPARATOR ',')"
        return f"GROUP_CONCAT({alias}.{col}, ',')"

    def _agg_ids_expr(self, alias: str, col: str = "id") -> str:
        url = settings.db.URL.lower()
        if url.startswith("postgres"):
            return f"STRING_AGG(CAST({alias}.{col} AS TEXT), ',')"
        if url.startswith("mysql"):
            return f"GROUP_CONCAT({alias}.{col} SEPARATOR ',')"
        return f"GROUP_CONCAT({alias}.{col}, ',')"

    async def paginate_cards(
        self,
        session: AsyncSession,
        page: int,
        size: int,
        category_id: Optional[int] = None,
        tag_id: Optional[int] = None,
    ) -> Tuple[List[dict], int]:
        where = []
        params: dict = {"limit": size, "offset": (page - 1) * size}
        if category_id is not None:
            where.append("p.id IN (SELECT post_id FROM post_categories WHERE category_id = :category_id)")
            params["category_id"] = category_id
        if tag_id is not None:
            where.append("p.id IN (SELECT post_id FROM post_tags WHERE tag_id = :tag_id)")
            params["tag_id"] = tag_id
        where_sql = (" WHERE " + " AND ".join(where)) if where else ""
        cat_ids_agg = self._agg_ids_expr("c")
        cat_names_agg = self._agg_names_expr("c")
        tag_ids_agg = self._agg_ids_expr("t")
        tag_names_agg = self._agg_names_expr("t")
        sql = f"""
        SELECT p.id, p.title, p.summary, p.author_name, p.created_at, p.updated_at, p.view_count, p.like_count,
               ({cat_ids_agg}) AS category_ids, ({cat_names_agg}) AS category_names,
               ({tag_ids_agg}) AS tag_ids, ({tag_names_agg}) AS tag_names
        FROM posts p
        LEFT JOIN post_categories pc ON pc.post_id = p.id
        LEFT JOIN categories c ON c.id = pc.category_id
        LEFT JOIN post_tags pt ON pt.post_id = p.id
        LEFT JOIN tags t ON t.id = pt.tag_id
        {where_sql}
        GROUP BY p.id, p.title, p.summary, p.author_name, p.created_at, p.updated_at, p.view_count, p.like_count
        ORDER BY p.published_at DESC, p.created_at DESC
        LIMIT :limit OFFSET :offset
        """
        total_sql = f"SELECT COUNT(*) FROM posts p{where_sql}"
        total = int((await session.execute(text(total_sql), params)).scalar() or 0)
        rows = (await session.execute(text(sql), params)).mappings().all()
        return [dict(r) for r in rows], total

    async def get_detail(self, session: AsyncSession, post_id: int) -> PostDetailVO | None:
        cat_ids_agg = self._agg_ids_expr("c")
        cat_names_agg = self._agg_names_expr("c")
        tag_ids_agg = self._agg_ids_expr("t")
        tag_names_agg = self._agg_names_expr("t")
        sql = f"""
        SELECT p.id, p.title, p.summary, p.author_name, p.created_at, p.updated_at, p.view_count, p.like_count,
               p.status, p.published_at, p.content_file_path,
               ({cat_ids_agg}) AS category_ids, ({cat_names_agg}) AS category_names,
               ({tag_ids_agg}) AS tag_ids, ({tag_names_agg}) AS tag_names
        FROM posts p
        LEFT JOIN post_categories pc ON pc.post_id = p.id
        LEFT JOIN categories c ON c.id = pc.category_id
        LEFT JOIN post_tags pt ON pt.post_id = p.id
        LEFT JOIN tags t ON t.id = pt.tag_id
        WHERE p.id = :post_id
        GROUP BY p.id, p.title, p.summary, p.author_name, p.created_at, p.updated_at, p.view_count, p.like_count,
                 p.status, p.published_at, p.content_file_path
        """
        row: RowMapping = (await session.execute(text(sql), {"post_id": post_id})).mappings().one()
        if not row:
            return None
        return PostDetailVO(**dict(row))

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
            await session.execute(insert(PostCategory), [{"post_id": post_id, "category_id": cid} for cid in category_ids])
            await session.commit()

    async def remove_categories(self, session: AsyncSession, post_id: int) -> None:
        """删除文章的所有分类关联。"""
        await session.execute(delete(PostCategory).where(PostCategory.post_id == post_id))
        await session.commit()

    async def add_tags(self, session: AsyncSession, post_id: int, tag_ids: Iterable[int]) -> None:
        """为文章新增标签关联：幂等插入，不负责删除。"""
        if tag_ids:
            await session.execute(insert(PostTag), [{"post_id": post_id, "tag_id": tid} for tid in tag_ids])
            await session.commit()

    async def remove_tags(self, session: AsyncSession, post_id: int) -> None:
        """删除文章的所有标签关联。"""
        await session.execute(delete(PostTag).where(PostTag.post_id == post_id))
        await session.commit()
