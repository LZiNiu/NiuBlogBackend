from typing import List, Tuple
from model.models import Article, User, Category
from model.article_api_models import ArticleIn, ArticleMeta, ArticleDetail
from sqlmodel import select, Session, func
from sqlalchemy.engine import Row
from model.db import get_session
from datetime import datetime
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # 获取项目根目录
DOCS_DIR = BASE_DIR / "docs"

# 创建文件夹（如果不存在）
os.makedirs(DOCS_DIR, exist_ok=True)
# 获取模型的所有字段
article_all_fields = Article.__annotations__.keys()


def create_new_article(article: ArticleIn):
    # 判断是否为较大的 Markdown 文件
    def is_large_markdown(content: str) -> bool:
        # 假设字数超过 5000 字为较大的 Markdown 文件
        return len(content) > 5000

    # 查找用户
    with next(get_session()) as session:
        user = session.get(User, article.author_id)
        if not user:
            return None
        # 创建 Article 实例
        new_article = Article(
            article_title=article.article_title,
            content=article.content if not is_large_markdown(article.content) else "",
            created_at=article.created_at,
            updated_at=article.updated_at,
            tags=article.tags,
            category_id=article.category_id,
            is_large_text=is_large_markdown(article.content),
            description=article.description if article.description else "",
            author_id=article.author_id,
        )
        new_article.author = user
        # user.articles.append(new_article)
        try:
            # 保存到数据库
            session.add(new_article)
            session.commit()
            session.refresh(new_article)

        except Exception as e:
            raise e
    # 如果是较大的 Markdown 文件，保存到文件系统
    if new_article.is_large_text:
        user_dir = DOCS_DIR / str(article.author_id)
        os.makedirs(user_dir, exist_ok=True)
        file_path = user_dir / f"{new_article.article_id}.md"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(article.content)
        new_article.content = file_path
        try:
            session.add(new_article)
            session.commit()
        except Exception as e:
            raise e

    return new_article


# 需要排除的字段(Article中没有的字段),不需要的字段已经通过类本身排除
excluded_fields = {"author_name", "category_name"}
# 选择meta需要的字段
meta_selected_fields = [getattr(Article, field)
                        for field in ArticleMeta.model_fields.keys() if field not in excluded_fields]
detail_selected_fields = [getattr(Article, field)
                          for field in ArticleDetail.model_fields.keys() if field not in excluded_fields]


def get_article_meta_by_id(
        user_id: int,
        page: int,
        page_size: int,
        session: Session) -> Tuple[List[ArticleMeta], int] | None:
    """
    获取文章基本信息
    :param user_id: 要查找的用户默认只有自己
    :param page: 当前页
    :param page_size: 页面大小
    :param session:
    :return: (对应用户的文章基本信息列表, 文章总数)
    """
    offset = (page - 1) * page_size
    limit = page_size
    statement = (
        # 查询 Article 和 User 的 username
        select(*meta_selected_fields,
               User.username.label("author_name"),
               Category.category_name.label("category_name"))
        .join(User, Article.author_id == User.id)
        .outerjoin(Category, Article.category_id == Category.id)  # 处理 category_id 为 NULL 的情况
        .where(User.id == user_id)
    )
    paginated_statement = statement.offset(offset).limit(limit)
    count_statement = select(func.count()).select_from(statement.subquery())
    total_count = int(session.exec(count_statement).one())
    results = session.exec(paginated_statement).all()  # 返回 [(Article, username), ...]
    return results, total_count


def get_article_content(article_id: int, session: Session):
    result = session.exec(select(Article.content, Article.is_large_text).where(Article.article_id == article_id)).one()
    is_large_text = result[1]
    if is_large_text:
        store_path = result[0]
        with open(store_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = result[0]
    return content


def get_article_detail(article_id: int, session: Session) -> ArticleDetail | None:
    """
    :param article_id: 文章id
    :param session:
    :return: 包含除is_large_text和author_id之外的对应id文章的所有信息
    """
    try:
        article = session.exec(
            select(*detail_selected_fields,
                   User.username.label("author_name"),
                   Category.category_name.label("category_name"),
                   Article.is_large_text)
            .join(User, Article.article_id == article_id).outerjoin(Category, Article.category_id == Category.id)
        ).first()
    except Exception as e:
        print(e)
        return None
    if article is not None:
        is_large_text = article[-1]
        if is_large_text:
            article = article._mapping
            store_path = article['content']
            with open(store_path, 'r', encoding='utf-8') as f:
                article['content'] = f.read()
            # 重新构造ArticleDetail对象
            article = ArticleDetail.construct(**article)
    return article


def get_all_articles() -> List[Article]:
    with next(get_session()) as session:
        statement = select(Article).order_by(Article.created_at)
        articles = session.exec(statement).all()
        return articles


def update_content(article_id: int):
    with next(get_session()) as session:
        article = session.get(Article, article_id)
        if article is None:
            return None
        if article.is_large_text:
            store_path = article.content
            with open(store_path, 'r', encoding='utf-8') as f:
                content = f.read()
            article.content = content
            session.add(article)
            session.commit()
            session.refresh(article)


def update_content_test(article_id: int = 1):
    with next(get_session()) as session:
        article = session.get(Article, article_id)
        if article is None:
            return None
        store_path = DOCS_DIR / "python_call_cxx.md"
        with open(store_path, 'r', encoding='utf-8') as f:
            content = f.read()
        article.content = content
        session.add(article)
        session.commit()
        session.refresh(article)
