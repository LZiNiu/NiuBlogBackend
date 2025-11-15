from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dao.UserMapper import UserMapper, get_user_mapper
from handler.exception_handlers import AuthenticationException
from model.db import get_session
from model.dto.user import (AdminCreateUserRequest, ChangePasswordRequest,
                            UpdateUserInfoRequest,
                            UserLoginRequest, UserLoginResponse,
                            UserRegisterDTO)
from model.entity.models import User
from model.common import JwtPayload
from model.vo.user import UserInfoVO, UserVerify
from services.base import BaseService
from utils.auth_utils import JwtUtil
from utils.cryptpwd import PasswordUtil


class UserService(BaseService):
    def __init__(self, session: AsyncSession, mapper: UserMapper):
        super().__init__(session)
        self.mapper = mapper

    async def register(self, userRegisterDTO: UserRegisterDTO):
        """
        注册
        :param userRegisterDTO:
        :return:    
        """
        # 构造user对象
        user = User(**userRegisterDTO.model_dump())
        user.password_hash = PasswordUtil.get_password_hash(userRegisterDTO.password)
        await self.mapper.create(self.session, user)

    async def authenticate(self, login_request: UserLoginRequest) -> UserLoginResponse:
        """
        用户认证：校验密码并在需要时自动升级哈希
        :param login_request: 用户登录请求（用户名+明文密码）
        :return: 登录响应（token + 用户信息）
        """
        # 查询用户（仅加载密码哈希字段）
        user = await self.mapper.get_one(self.session, 
                                fields=self.mapper.select_fields(User, UserVerify), 
                                username=login_request.username)
        if not user or not user.is_active:
            self.logger.warning("认证失败：用户不存在或未激活 username=%s", login_request.username)
            raise AuthenticationException("用户名或密码错误")

        # 验证密码并自动升级哈希
        ok, new_hash = PasswordUtil.verify_and_upgrade(login_request.password, user.password_hash)
        if not ok:
            self.logger.warning("认证失败：密码错误 username=%s", login_request.username)
            raise AuthenticationException("用户名或密码错误")

        if new_hash is not None:
            # 透明升级哈希，提升安全性
            await self.mapper.update(self.session, user.id, {"password_hash": new_hash})  # type: ignore
            self.logger.info("已升级用户密码哈希 username=%s", login_request.username)

        payload = JwtPayload(user_id=user.id, username=user.username, role=user.role)
        access, refresh = JwtUtil.issue_token_pair(payload)
        self.logger.info("用户登录成功 username=%s", login_request.username)
        return UserLoginResponse(
            token=access,
            refreshToken=refresh
        )

    def logout(self, token: str) -> None:
        """
        登出：撤销令牌（加入黑名单直到过期）
        """
        ok = JwtUtil.revoke_token(token)
        if ok:
            self.logger.info("用户登出成功，令牌已撤销")
        else:
            self.logger.warning("用户登出失败，令牌无效或已过期")

    async def admin_create_user(self, req: AdminCreateUserRequest) -> int:
        """
        管理员创建用户
        :param actor_id: 执行操作的管理员ID
        :param req: 用户创建请求
        :return: 创建的用户ID
        """
        # 创建用户
        user = User(**req.model_dump())
        user.password_hash = PasswordUtil.get_password_hash(req.password)
        await self.mapper.create(self.session, user)
        return user.id
    
    async def paginate_users_vo(self, page: int = 1, page_size: int = 10) -> tuple[list[UserInfoVO | dict], int]:
        """
        管理员分页查询所有用户信息
        :param actor_id: 执行操作的管理员ID
        :return: 用户信息列表
        """
        # 查询所有用户
        users, total = await self.mapper.paginate(self.session, page, page_size, fields=UserInfoVO)
        return users, total

    async def get_user_by_id(self, user_id: int) -> UserInfoVO | dict | None:
        """
        管理员查询指定用户信息
        :param actor_id: 执行操作的管理员ID
        :param user_id: 用户ID
        :return: 用户信息
        """
        # 查询用户
        user = await self.mapper.get_user_info_by_id(self.session, user_id=user_id)
        return user

    async def get_user_info(self, user_id: int) -> UserInfoVO:
        data = await self.mapper.get_user_info_by_id(self.session, user_id=user_id)
        if not data:
            raise AuthenticationException("用户不存在")
        return UserInfoVO(**data)

    async def update_user_info(self, user_id: int, req: UpdateUserInfoRequest) -> UserInfoVO:
        update_dict = req.model_dump(exclude_unset=True)
        obj = await self.mapper.update(self.session, user_id, update_dict)
        if not obj:
            raise AuthenticationException("用户不存在")
        return UserInfoVO.model_validate(obj)

    async def change_password(self, user_id: int, req: ChangePasswordRequest) -> None:
        user = await self.mapper.get_by_id(self.session, user_id)
        if not user:
            raise AuthenticationException("用户不存在")
        ok, _ = PasswordUtil.verify_and_upgrade(req.old_password, user.password_hash)
        if not ok:
            raise AuthenticationException("旧密码错误")
        new_hash = PasswordUtil.get_password_hash(req.new_password)
        await self.mapper.update(self.session, user_id, {"password_hash": new_hash})

    def refresh_tokens(self, refresh_token: str) -> UserLoginResponse:
        access, refresh = JwtUtil.refresh_token_pair(refresh_token)
        if not access or not refresh:
            raise AuthenticationException("刷新令牌无效或已过期")
        return UserLoginResponse(token=access, refreshToken=refresh)

    async def update_user_status(self, user_id: int, status: bool) -> UserInfoVO:
        obj = await self.mapper.update(self.session, user_id, {"is_active": status})
        if not obj:
            raise AuthenticationException("用户不存在")
        return UserInfoVO.model_validate(obj)

    async def delete_user(self, user_id: int) -> None:
        ok = await self.mapper.delete(self.session, user_id)
        if not ok:
            raise AuthenticationException("用户不存在")


def get_user_service(session: AsyncSession = Depends(get_session), mapper: UserMapper = Depends(get_user_mapper)) -> UserService:
    """
    获取用户服务实例
    :param session: 数据库会话
    :return: UserService实例
    """
    service = UserService(session, mapper)
    return service
