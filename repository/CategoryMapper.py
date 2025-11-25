from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from model.orm.models import Category
from .BaseMapper import BaseMapper


class CategoryMapper(BaseMapper[Category]):
    def __init__(self):
        super().__init__(Category)

    async def list_all(self, session: AsyncSession) -> List[Category]:
        result = await session.execute(
                                select(*Category.__table__.columns)
                                .order_by(Category.create_time.desc()))
        return [dict(row) for row in result.mappings()]
