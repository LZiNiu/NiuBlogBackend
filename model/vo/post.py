from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from services import tag


class SimpleCategoryVO(BaseModel):
    id: int
    name: str


class PostCardVO(BaseModel):
    id: int
    title: str
    summary: Optional[str] = None
    author_name: str
    created_at: datetime
    updated_at: datetime
    view_count: int
    like_count: int
    tag_ids: str | None = None
    tag_names: str | None = None
    category_ids: str | None = None
    categorie_names: str | None = None

    class Config:
        from_attributes = True


class PostDetailVO(PostCardVO):
    status: str
    published_at: Optional[datetime] = None
    content_file_path: str
    body_text: Optional[str] = None

    class Config:
        from_attributes = True


class PostBodyMetaVO(BaseModel):
    """正文文件元信息"""
    path: str
    size: int
    mime: str
