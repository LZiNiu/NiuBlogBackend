from functools import lru_cache
from .BaseMapper import BaseMapper
from model.user import User


class UserMapper(BaseMapper[User]):
    def __init__(self):
        super().__init__(User)


@lru_cache(maxsize=1)
def get_user_mapper() -> UserMapper:
    return UserMapper()
