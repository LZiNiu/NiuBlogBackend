from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Category(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    create_time: datetime | None = None
    update_time: datetime | None = None
