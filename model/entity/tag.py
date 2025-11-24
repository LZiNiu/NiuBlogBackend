from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: Optional[str] = None
    color: Optional[str] = None
    create_time: datetime
    update_time: datetime

class TagCreate(BaseModel):
    name: str
    slug: Optional[str] = None
    color: Optional[str] = None

class TagUpdate(BaseModel):
    slug: Optional[str] = None
    color: Optional[str] = None