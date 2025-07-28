from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.dialects.mysql import TEXT


class User(SQLModel, table=True):
    """
    用户表
    由于是个人博客,只有网站主人写文章,游客只发表评论,所以实际上只有1个人有文章,采用简单的外键形式连接用户和文章
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, description="用户名")
    password: str = Field(index=True)
    avatar: Optional[str] = Field(default=None, sa_column_kwargs={"comment": "用户头像url"})

    # 通过关联表连接文章
    articles: List["Article"] = Relationship(back_populates="author")


class Category(SQLModel, table=True):
    """
    文章分类表
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    category_name: str = Field(unique=True, sa_column_kwargs={"comment": "分类名"})


class Article(SQLModel, table=True):
    article_id: Optional[int] = Field(default=None, primary_key=True)
    article_title: str = Field(index=True, description="文章标题")
    content: str = Field(default="", sa_type=TEXT)
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    tags: Optional[str] = Field(default=None, index=True)
    category_id: Optional[int] = Field(default=None, index=True, foreign_key="category.id")
    is_large_text: bool = Field()
    description: Optional[str] = Field(default=None, sa_type=TEXT)
    author_id: int | None = Field(default=None, foreign_key="user.id")
    # (项目的文章作者仅有本人)
    author: User = Relationship(back_populates="articles")
    category: Category = Relationship()

    def update_timestamp(self):
        """更新 updated_at 字段"""
        self.updated_at = datetime.now()







