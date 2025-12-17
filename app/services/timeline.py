from fastapi import Depends

from app.db.session import AsyncSession, get_session
from app.model.entity import Timeline
from app.repository import TimelineMapper, get_timeline_mapper

from .base import BaseService

class TimelineService(BaseService[TimelineMapper]):
    def __init__(self, session: AsyncSession, mapper):
        super().__init__(session, mapper)

    async def list_all(self) -> list[Timeline | dict]:
        items = await self.mapper.list_all(self.session)
        return items


def get_timeline_service(session: AsyncSession = Depends(get_session), 
                            mapper: TimelineMapper = Depends(get_timeline_mapper)) -> TimelineService:
    return TimelineService(session, mapper)
