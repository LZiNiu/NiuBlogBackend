from typing import Optional

from pydantic import BaseModel


class CommentCreateDTO(BaseModel):
    content: str
    parent_id: Optional[int] = None
