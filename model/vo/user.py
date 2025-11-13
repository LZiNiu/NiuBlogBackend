from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

# ==================== VO 模型 ====================

class UserInfoVO(BaseModel):
    """用户信息响应 VO"""
    id: int
    username: str
    email: EmailStr
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # 允许从 ORM 模型实例创建