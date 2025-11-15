from typing import List

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dao.CategoryMapper import CategoryMapper
from model.db import get_session
from model.vo.category import CategoryVO
from services.base import BaseService


def get_category_mapper() -> CategoryMapper:
    return CategoryMapper()


class CategoryService(BaseService):
    def __init__(self, session: AsyncSession, mapper: CategoryMapper):
        super().__init__(session)
        self.mapper = mapper

    async def list_all(self) -> List[CategoryVO | dict]:
        items = await self.mapper.list_all(self.session)
        return [CategoryVO.model_validate(i).model_dump() for i in items]


def get_category_service(session: AsyncSession = Depends(get_session), mapper: CategoryMapper = Depends(get_category_mapper)) -> CategoryService:
    return CategoryService(session, mapper)
