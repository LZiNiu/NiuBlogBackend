from typing import List
from model.models import User
from model.article_api_models import ArticleMeta
from sqlmodel import select
from model.db import get_session
from typing import Union


def create_user(user_name: str, pw: str, avatar: str = None):
    with next(get_session()) as session:
        user = User(username=user_name, password=pw, avatar=avatar)
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


def get_all_user() -> List[User]:
    with next(get_session()) as session:
        users = session.exec(select(User))
        return users.all()


def get_user_by_id(user_id: int) -> User:
    with next(get_session()) as session:
        user = session.get(User, user_id)
        return user


def get_user_by_name(user_name: str) -> List[User]:
    with next(get_session()) as session:
        result = session.exec(select(User).where(User.username == user_name))
        users = result.all()
        return users


def get_article_meta_by_user_id(user_id: int) -> ArticleMeta | None:
    with next(get_session()) as session:
        user = session.get(User, user_id)
        articles = user.articles
        return articles
