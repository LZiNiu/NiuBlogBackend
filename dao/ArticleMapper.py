from typing import Type

from sqlalchemy import Row
from .BaseMapper import BaseMapper
from model.entity import Post
from sqlmodel import Session


class PostMapper(BaseMapper):
    def __init__(self, model: Type[Post]):
        super().__init__(model)

    def get_posts_info(self, session: Session, author_id: int):
        statement = self.select_fields(Post, PostInfoVO).where(Post.author_id == author_id)
        result: list[Row] = session.exec(statement).all()
        return [row._asdict() for row in result]