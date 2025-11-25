from typing import List

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from model.orm.models import Tag
from .BaseMapper import BaseMapper


class TagMapper(BaseMapper[Tag]):
    def __init__(self):
        super().__init__(Tag)

    async def list_all(self, session: AsyncSession) -> List[Tag]:
        result = await session.execute(select(Tag).order_by(Tag.create_time.desc()))
        return list(result.scalars().all())

    async def insert_batch(self, session: AsyncSession, tag_names: List[str]) -> None:
        await session.execute(insert(Tag).values([{'name': name} for name in tag_names]))
        await session.commit()
