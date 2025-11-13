from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .BaseMapper import BaseMapper
from model.user import User, UserInfoVO


class UserMapper(BaseMapper[User]):
    def __init__(self):
        super().__init__(User)

    async def list_users_info(self, session: AsyncSession, page: int = 1, page_size: int = 10) -> list[UserInfoVO]:
        """
        查询所有用户
        :param session: 数据库会话
        :return: 用户列表
        """
        stmt = self.select_fields(User, UserInfoVO).offset((page - 1) * page_size).limit(page_size)
        result = await session.execute(stmt)
        rows = result.all()
        return [row._asdict() for row in rows]

    async def get_user_info_by_id(self, session: AsyncSession, user_id: int) -> UserInfoVO | None:
        """
        根据用户ID查询用户信息
        :param session: 数据库会话
        :param user_id: 用户ID
        :return: 用户信息
        """
        stmt = self.select_fields(User, UserInfoVO).where(User.id == user_id)
        result = await session.execute(stmt)
        row = result.first()
        return row._asdict() if row else None

@lru_cache(maxsize=1)
def get_user_mapper() -> UserMapper:
    return UserMapper()
