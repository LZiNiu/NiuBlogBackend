from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr
from app.model.orm.field_enum import Role

# ==================== VO 模型 ====================
class UserVerify(BaseModel):
    """用户验证 VO"""
    id: int
    username: str
    password_hash: str
    role: Role
    is_active: int

class UserInfoVO(BaseModel):
    """用户信息响应 VO"""
    id: int
    username: str
    email: EmailStr
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    role: Role
    is_active: int
    create_time: datetime
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True  # 允许从 ORM 模型实例创建