from functools import lru_cache

from sqlalchemy import Row
from .BaseMapper import BaseMapper
from model.user import User, UserInfoVO
from sqlmodel import Session, select


class UserMapper(BaseMapper[User]):
    def __init__(self):
        super().__init__(User)

    def list_users_info(self, session: Session, page: int = 1, page_size: int = 10) -> list[UserInfoVO]:
        """
        查询所有用户
        :param session: 数据库会话
        :return: 用户列表
        """
        result: list[Row] = session.exec(self.select_fields(User, UserInfoVO)
                                .offset((page - 1) * page_size)
                                .limit(page_size)).all()
        return [user._asdict() for user in result]

    def get_user_info_by_id(self, session: Session, user_id: int) -> UserInfoVO | None:
        """
        根据用户ID查询用户信息
        :param session: 数据库会话
        :param user_id: 用户ID
        :return: 用户信息
        """
        result: Row = session.exec(self.select_fields(User, UserInfoVO)
                                .where(User.id == user_id)).first()
        return result._asdict() if result else None

@lru_cache(maxsize=1)
def get_user_mapper() -> UserMapper:
    return UserMapper()
