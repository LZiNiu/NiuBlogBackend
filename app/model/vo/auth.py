from pydantic import BaseModel


class UserLoginResponse(BaseModel):
    """用户登录响应 DTO"""
    token: str # 访问令牌
    refreshToken: str # 刷新令牌


class RefreshTokenRequest(BaseModel):
    refreshToken: str