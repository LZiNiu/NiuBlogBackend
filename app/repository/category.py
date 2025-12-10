from typing import List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.orm.models import Category, PostCategory
from app.model.vo import CategoryCardVO
from .base import BaseMapper


class CategoryMapper(BaseMapper[Category]):
    def __init__(self):
        super().__init__(Category)

    async def list_all(self, session: AsyncSession) -> List[Category]:
        result = await session.execute(
                                select(*Category.__table__.columns)
                                .order_by(Category.create_time.desc()))
        return [dict(row) for row in result.mappings()]

    async def list_cards(self, session: AsyncSession) -> List[CategoryCardVO]:
        stmt = select(*self.select_fields(Category, CategoryCardVO), 
                        func.count(PostCategory.category_id).label("article_count")) \
                        .select_from(Category) \
                        .join(PostCategory, Category.id == PostCategory.category_id, isouter=True) \
                        .group_by(Category.id)
        result = await session.execute(stmt)
        return [CategoryCardVO(**dict(row)) for row in result.mappings()]



_category_mapper = CategoryMapper()
def get_category_mapper() -> CategoryMapper:
    return _category_mapper
