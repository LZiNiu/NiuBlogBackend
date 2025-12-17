from typing import List

from sqlalchemy import Row, select, insert, Result
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.orm.models import Timeline as TimelineORM
from app.model.entity.models import Timeline
from .base import BaseMapper


class TimelineMapper(BaseMapper[TimelineORM]):
    def __init__(self):
        super().__init__(TimelineORM)

    async def list_all(self, session: AsyncSession) -> List[Timeline]:
        result: Result[Row] = await session.execute(select(*TimelineORM.__table__.c).order_by(TimelineORM.date.desc()))
        return [Timeline(**dict(row)) for row in result.mappings().all()]


_timeline_mapper = TimelineMapper()

def get_timeline_mapper() -> TimelineMapper:
    return _timeline_mapper
