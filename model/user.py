from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr
from sqlmodel import Field, SQLModel

# ==================== 表模型 ====================

class UserBase(SQLModel):
    """用户基础信息"""
    username: str = Field(unique=True, nullable=False, min_length=3, max_length=50)
    email: EmailStr = Field(unique=True)
    nickname: Optional[str] = Field(default=None, max_length=100)
    avatar_url: Optional[str] = Field(default="./resource/avatar/default.jpg", max_length=255)
    bio: Optional[str] = Field(default=None)
    role: str = Field(default="user")
    is_active: bool = Field(default=True)


class User(UserBase, table=True):
    """用户表模型"""
    __tablename__ = "users"  # type: ignore
    
    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str = Field(nullable=False, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


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
