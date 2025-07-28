from pydantic import BaseModel
from datetime import datetime


class ArticleBase(BaseModel):
    article_title: str
    created_at: datetime
    updated_at: datetime
    tags: str | None
    category_id: int | None
    description: str | None


class ArticleIn(ArticleBase):
    """
    文章接口的输入,有必要知道文章的基本信息以及对应的user_id
    """
    # 不能为空
    author_id: int
    content: str
    description: str | None


class ArticleMeta(ArticleBase):
    """
    文章基本信息,用于文章卡片渲染,需要展示作者的名字
    在点击卡片时需要根据文章id请求具体内容,此时与user方无关
    """
    article_id: int | None = None
    author_name: str | None = None
    category_name: str | None = None


class ArticleDetail(ArticleMeta):
    """
    文章基本信息,用于文章卡片渲染,需要展示作者的名字
    在点击卡片时需要根据文章id请求具体内容,此时与user方无关,没有author_id和is_large_text字段
    """
    content: str | None = None