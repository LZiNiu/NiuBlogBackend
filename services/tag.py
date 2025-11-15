from typing import List

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dao.TagMapper import TagMapper
from model.db import get_session
from model.vo.tag import TagVO
from services.base import BaseService


def get_tag_mapper() -> TagMapper:
    return TagMapper()


class TagService(BaseService):
    def __init__(self, session: AsyncSession, mapper: TagMapper):
        super().__init__(session)
        self.mapper = mapper

    async def list_all(self) -> List[TagVO | dict]:
        items = await self.mapper.list_all(self.session)
        return [TagVO.model_validate(i).model_dump() for i in items]


def get_tag_service(session: AsyncSession = Depends(get_session), mapper: TagMapper = Depends(get_tag_mapper)) -> TagService:
    return TagService(session, mapper)
