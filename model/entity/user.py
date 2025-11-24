from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, field_serializer, Field
from model.enums import Role

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: EmailStr
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    role: Role
    status: int = Field(alias='status', default=1)
    create_time: datetime
    update_time: datetime
    @field_serializer('role')
    def serialize_role(self, v: Role):
        return v.value

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    role: Optional[Role] = None

class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    role: Optional[Role] = None
    status: Optional[bool] = None