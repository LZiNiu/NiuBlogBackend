from typing import Optional

from pydantic import BaseModel, EmailStr

from model.orm.models import Role


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


class UpdateUserInfoRequest(BaseModel):
    """更新用户信息请求 DTO"""
    nickname: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None

class UpdateUserStatus(BaseModel):
    is_active: bool

class ChangePasswordRequest(BaseModel):
    """修改密码请求 DTO"""
    old_password: str
    new_password: str


class AdminCreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    nickname: Optional[str] = None
    role: Role = Role.USER
    avatar_url: Optional[str] = None
