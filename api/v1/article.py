from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from model.article_api_models import ArticleIn, ArticleMeta, ArticleDetail
from services.article import get_article_meta_by_id, get_article_content, create_new_article, get_article_detail
from model.db import get_session
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/article", tags=["article"])


@router.post("/create", response_model=ArticleMeta)
def create_article(article: ArticleIn, session: Session = Depends(get_session)):
    """
    创建文章接口仅暴露给管理员使用
    :param session:
    :param article: 文章信息 包含
                            author_id: int
                            article_title: str
                            content: str
                            created_at: datetime
                            updated_at: datetime
                            tags: str | None
                            category: str | None
                            description: str | None
    :return:
    """
    new_article = create_new_article(article)
    if new_article is None:
        raise HTTPException(status_code=204, detail="用户非法")
    return new_article


class ArticleMetaOut(BaseModel):
    article_list: list[ArticleMeta]
    total: int


@router.get("/getMeta", response_model=ArticleMetaOut)
def get_article_meta(page: int = 1, page_size: int = 5, session: Session = Depends(get_session)):
    author_id = 1
    articles, total = get_article_meta_by_id(author_id, page, page_size, session)
    if articles is None:
        # 用户没有文章返回空列表
        articles = []
    return {"article_list": articles, "total": total}  # 返回元组


@router.get("/getSingleContent/{article_id}")
def get_content(article_id: int, session: Session = Depends(get_session)):
    content = get_article_content(article_id, session)
    return {
        "msg": "success",
        "article_id": article_id,
        "content": content
    }


@router.get("/getSingleDetail/{article_id}", response_model=ArticleDetail)
def get_detail(article_id: int, session: Session = Depends(get_session)):
    article = get_article_detail(article_id, session)
    if article is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    return article
