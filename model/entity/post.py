from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_serializer
from model.enums import PostStatus

class PostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    summary: Optional[str] = None
    cover_image_url: Optional[str] = None
    content_file_path: str
    author_id: int
    author_name: Optional[str] = None
    status: PostStatus
    view_count: int
    like_count: int
    published_at: Optional[datetime] = None
    reading_time: int
    is_featured: bool
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    last_commented_at: Optional[datetime] = None
    create_time: datetime
    update_time: datetime
    @field_serializer('status')
    def serialize_status(self, v: PostStatus):
        return v.value

class PostCreate(BaseModel):
    title: str
    summary: Optional[str] = None
    cover_image_url: Optional[str] = None
    content_file_path: str
    author_id: int
    author_name: Optional[str] = None
    status: Optional[PostStatus] = None

class PostUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    cover_image_url: Optional[str] = None
    content_file_path: Optional[str] = None
    author_name: Optional[str] = None
    status: Optional[PostStatus] = None
    reading_time: Optional[int] = None
    is_featured: Optional[bool] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None