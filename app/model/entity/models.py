from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date as pydate
from app.model.orm.field_enum import Role, PostStatus, TimelineEvent
# ==================== Pydantic Models (v2) ====================

class User(BaseModel):
    id: int | None = None
    username: str
    email: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = "./resource/avatar/default.jpg"
    bio: Optional[str] = None
    role: Role = Role.USER
    is_active: int = 1  # 注意：ORM 中数据库列名为 "status"，但模型字段名为 is_active
    password_hash: str | None = None
    create_time: datetime | None = None
    update_time: datetime | None = None

    model_config = {"from_attributes": True}


class Category(BaseModel):
    id: int | None = None
    name: str
    description: Optional[str] = None
    create_time: datetime | None = None
    update_time: datetime | None = None

    model_config = {"from_attributes": True}


class Tag(BaseModel):
    id: int | None = None
    name: str
    create_time: datetime | None = None
    update_time: datetime | None = None

    model_config = {"from_attributes": True}


class Post(BaseModel):
    id: int | None = None
    title: str
    summary: Optional[str] = None
    cover_image_url: Optional[str] = None
    content_file_path: str
    author_id: int | None
    author_name: str
    post_status: PostStatus = PostStatus.DRAFT  # ORM 中列名为 "status"
    view_count: int = 0
    like_count: int = 0
    create_time: datetime | None = None
    update_time: datetime | None = None

    model_config = {"from_attributes": True}


class PostCategory(BaseModel):
    post_id: int
    category_id: int

    model_config = {"from_attributes": True}


class PostTag(BaseModel):
    post_id: int
    tag_id: int

    model_config = {"from_attributes": True}


class Timeline(BaseModel):
    id: int | None = None
    date: pydate | None
    title: str
    content: Optional[str] = None
    images: Optional[list[str]] = None
    event_type: str = TimelineEvent.coding
    link: Optional[str] = None
