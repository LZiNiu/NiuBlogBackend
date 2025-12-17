from typing import List

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.orm.models import Tag
from .base import BaseMapper


class TagMapper(BaseMapper[Tag]):
    def __init__(self):
        super().__init__(Tag)

    async def list_all(self, session: AsyncSession) -> List[Tag]:
        result = await session.execute(select(Tag).order_by(Tag.create_time.desc()))
        return list(result.scalars().all())


_tag_mapper = TagMapper()

def get_tag_mapper() -> TagMapper:
    return _tag_mapper
