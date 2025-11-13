from functools import lru_cache

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from model.entity.models import User
from model.vo.user import UserInfoVO

from .BaseMapper import BaseMapper


class UserMapper(BaseMapper[User]):
    def __init__(self):
        super().__init__(User)

    async def get_user_info_by_id(self, session: AsyncSession, user_id: int) -> dict | None:
        """
        根据用户ID查询用户信息
        :param session: 数据库会话
        :param user_id: 用户ID
        :return: 用户信息
        """
        stmt = select(*self.select_fields(User, UserInfoVO)).where(User.id == user_id)
        result = await session.execute(stmt)
        row = result.first()
        return row._asdict() if row else None

@lru_cache(maxsize=1)
def get_user_mapper() -> UserMapper:
    return UserMapper()
