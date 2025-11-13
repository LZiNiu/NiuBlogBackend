from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, DateTime

from .common import Base
# ==================== 表模型 ====================

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    nickname: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, default="./resource/avatar/default.jpg")
    bio: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)


    def __repr__(self) -> str:
        return f"<User id={getattr(self, 'id', None)} username={self.username}>"


# ==================== DTO 模型 ====================

class UserRegisterDTO(BaseModel):
    """用户注册请求 DTO"""
    username: str
    email: EmailStr
    password: str
    nickname: Optional[str] = None


class UserLoginRequest(BaseModel):
    """用户登录请求 DTO"""
    username: str
    password: str


class UserLoginResponse(BaseModel):
    """用户登录响应 DTO"""
    access_token: str
    token_type: str
    user_info: "UserInfoVO"


class UpdateUserInfoRequest(BaseModel):
    """更新用户信息请求 DTO"""
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    """修改密码请求 DTO"""
    old_password: str
    new_password: str


class UpdateUserStatusRequest(BaseModel):
    """更新用户状态请求 DTO"""
    is_active: bool

class AdminCreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    nickname: Optional[str] = None
    role: str = "user"


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



# 解决向前引用问题
UserLoginResponse.model_rebuild()
