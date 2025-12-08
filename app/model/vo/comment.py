from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CommentVO(BaseModel):
    id: int
    post_id: int
    content: str
    author_user_id: int
    parent_id: Optional[int] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
