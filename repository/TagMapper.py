from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from model.orm.models import Tag
from .BaseMapper import BaseMapper


class TagMapper(BaseMapper[Tag]):
    def __init__(self):
        super().__init__(Tag)

    async def list_all(self, session: AsyncSession) -> List[Tag]:
        result = await session.execute(select(Tag).order_by(Tag.created_at.desc()))
        return list(result.scalars().all())
