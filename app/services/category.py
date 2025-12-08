from typing import List

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository import CategoryMapper
from app.db.session import get_session
from app.model.vo import CategoryVO, CategoryCardVO
from app.services.base import BaseService


def get_category_mapper() -> CategoryMapper:
    return CategoryMapper()


class CategoryService(BaseService):
    def __init__(self, session: AsyncSession, mapper: CategoryMapper):
        super().__init__(session)
        self.mapper = mapper

    async def list_all(self) -> List[CategoryVO | dict]:
        items = await self.mapper.list_all(self.session)
        return [CategoryVO.model_validate(i).model_dump() for i in items]
    
    async def list_cards(self) -> List[CategoryCardVO | dict]:
        items = await self.mapper.list_cards(self.session)
        return [CategoryCardVO.model_validate(i).model_dump() for i in items]

    async def paginated_categories(self, current: int, size: int):
        items, total = await self.mapper.paginate(self.session, current, size)
        return items, total


def get_category_service(session: AsyncSession = Depends(get_session), mapper: CategoryMapper = Depends(get_category_mapper)) -> CategoryService:
    return CategoryService(session, mapper)
