from typing import List, Optional

from pydantic import BaseModel

from app.model.orm.field_enum import PostStatus


class PostCreateDTO(BaseModel):
    title: str
    summary: str | None = None
    content: str | None = None
    post_status: PostStatus
    category_ids: List[int] | None = None
    tag_ids: List[int] | None = None
    category_names: List[str] | None = None
    tag_names: List[str] | None = None


class PostUpdateDTO(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    author_name: Optional[str] = None
    content: Optional[str] = None
    post_status: PostStatus | None = None
    category_ids: List[int] | None = []
    tag_ids: List[int] | None = []
