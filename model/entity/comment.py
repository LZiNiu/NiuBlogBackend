from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_serializer
from model.enums import CommentStatus

class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    post_id: int
    author_user_id: int
    content: str
    parent_id: Optional[int] = None
    status: CommentStatus
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_pinned: bool
    create_time: datetime
    update_time: datetime
    @field_serializer('status')
    def serialize_status(self, v: CommentStatus):
        return v.value

class CommentCreate(BaseModel):
    post_id: int
    author_user_id: int
    content: str
    parent_id: Optional[int] = None
    status: Optional[CommentStatus] = None