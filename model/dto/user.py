from typing import Optional

from pydantic import BaseModel, EmailStr

from model.vo.user import UserInfoVO

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


class AdminCreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    nickname: Optional[str] = None
    role: str = "user"