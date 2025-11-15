from typing import List, Optional

from pydantic import BaseModel


class PostCreateDTO(BaseModel):
    title: str
    summary: Optional[str] = None
    content_file_path: str
    status: Optional[str] = None
    category_ids: List[int] = []
    tag_ids: List[int] = []


class PostUpdateDTO(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    content_file_path: Optional[str] = None
    status: Optional[str] = None
    category_ids: Optional[List[int]] = None
    tag_ids: Optional[List[int]] = None
