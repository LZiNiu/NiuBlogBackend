from sqlalchemy.ext.asyncio import AsyncSession
from typing import TypeVar, Generic

from app.utils.logger import get_logger
from app.repository.base import BaseMapper


MapperType = TypeVar("MapperType", bound=BaseMapper)

class BaseService(Generic[MapperType]):
    def __init__(self, session: AsyncSession, mapper: MapperType):
        self.session = session
        self.mapper = mapper
        self.logger = get_logger(self.__class__.__name__)

    async def count(self,) -> int:
        return await self.mapper.count(self.session)
