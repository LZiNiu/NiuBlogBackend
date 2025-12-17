from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, TypeVar, Generic

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
    
    async def create(self, entity: dict[str, Any] | BaseModel) -> int:
        obj_id = await self.mapper.create(self.session, entity)
        return obj_id

    async def update(self, id: int, entity: dict[str, Any] | BaseModel) -> bool:
        if isinstance(entity, BaseModel):
            data = entity.model_dump()
        else:
            data = dict(entity)
        row_count = await self.mapper.update(self.session, id, data)
        return row_count > 0

    async def deleteById(self, id: int) -> bool:
        row_count = await self.mapper.delete(self.session, id)
        return row_count > 0
    
    async def deleteByIds(self, ids: list[int]) -> bool:
        row_count = await self.mapper.delete_batch(self.session, ids)
        return row_count > 0
