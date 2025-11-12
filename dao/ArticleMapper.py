from typing import Type

from sqlalchemy import Row
from .BaseMapper import BaseMapper
from model.article import Article
from sqlmodel import Session, SQLModel, select


class ArticleMapper(BaseMapper):
    def __init__(self, model: Type[Article]):
        super().__init__(model)

    def get_articles_info(self, session: Session, author_id: int):
        statement = self.select_fields(Article, ArticleInfoVO).where(Article.author_id == author_id)
        result: list[Row] = session.exec(statement).all()
        return [row._asdict() for row in result]