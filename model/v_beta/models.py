from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel


class ResponseStatus(BaseModel):
    code: int
    msg: str


class ArticleAuthor(SQLModel, table=True):
    """
    关联表：用于建立 User 和 Article 的多对多关系
    """
    __tablename__ = "article_author"

    article_id: int | None = Field(default=None, foreign_key="article.article_id", primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    author_name: str | None = Field(default=None, description="作者名称（用于用户注销后保留）")


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, description="用户名")
    password: str = Field(index=True)
    avatar: Optional[str] = Field(default=None, sa_column_kwargs={"comment": "用户头像url"})

    # 通过关联表连接文章
    articles: List["Article"] = Relationship(
        back_populates="authors",
        link_model=ArticleAuthor  # 指定关联表
    )


class UserResponse(BaseModel):
    username: str
    avatar: str | None


class Article(SQLModel, table=True):
    article_id: Optional[int] = Field(default=None, primary_key=True)
    article_title: str = Field(index=True, description="文章标题")
    content: str = Field(default="")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    tags: Optional[str] = Field(default=None, index=True)
    category: Optional[str] = Field(default=None, index=True)
    is_large_text: bool = Field()

    # 通过关联表连接用户
    authors: List["User"] = Relationship(
        back_populates="articles",
        link_model=ArticleAuthor  # 指定关联表
    )


class ArticleIn(BaseModel):
    author_id: int
    article_title: str
    content: str
    created_at: datetime
    updated_at: datetime
    tags: str | None
    category: str | None


class ArticleMeta(BaseModel):
    article_id: int | None = None
    author_id: int | None = None
    article_title: str = ''
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    tags: str | None = None
    category: str | None = None


