from typing import List

from pydantic import BaseModel, Field

from app.model.orm.field_enum import PostStatus


class PostCreate(BaseModel):
    title: str = Field(default="", description="文章标题")
    summary: str | None = Field(default=None, description="文章摘要")
    content: str | None = Field(default=None, description="文章内容")
    post_status: PostStatus = Field(default=PostStatus.DRAFT, description="文章状态")
    category_ids: List[int] | None = Field(default=None, description="文章分类id列表")
    tag_ids: List[int] | None = Field(default=None, description="文章标签id列表")
    category_names: List[str] | None = Field(default=None, description="文章分类名称列表")
    tag_names: List[str] | None = Field(default=None, description="文章标签名称列表")


class PostUpdate(BaseModel):
    title: str| None = Field(default=None, description="文章标题")
    summary: str | None = Field(default=None, description="文章摘要")
    author_name: str | None = Field(default=None, description="文章作者名称")
    content: str | None = Field(default=None, description="文章内容")
    post_status: PostStatus | None = Field(default=None, description="文章状态")
    category_ids: List[int] | None = Field(default=None, description="文章分类id列表")
    tag_ids: List[int] | None = Field(default=None, description="文章标签id列表")
