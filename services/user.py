from fastapi import Depends
from sqlmodel import Session

from handler.exception_handlers import AuthenticationException
from dao.UserMapper import UserMapper, get_user_mapper
from services.base import BaseService
from model.db import get_session
from model.common import JwtPayload
from model.user import User, UserRegisterDTO
from model.user import UserLoginRequest, UserLoginResponse, UserInfoVO, AdminCreateUserRequest
from utils.cryptpwd import get_password_hash, verify_and_upgrade
from utils.auth_utils import create_access_token
from utils.auth_utils import revoke_token


class UserService(BaseService):
    def __init__(self, session: Session, mapper: UserMapper):
        super().__init__(session)
        self.mapper = mapper

    def register(self, userRegisterDTO: UserRegisterDTO):
        """
        注册
        :param userRegisterDTO:
        :return:    
        """
        # 构造user对象
        user = User(**userRegisterDTO.model_dump())
        user.password_hash = get_password_hash(userRegisterDTO.password)
        self.mapper.create(self.session, user)

    def authenticate(self, login_request: UserLoginRequest) -> UserLoginResponse:
        """
        用户认证：校验密码并在需要时自动升级哈希
        :param login_request: 用户登录请求（用户名+明文密码）
        :return: 登录响应（token + 用户信息）
        """
        # 查询用户
        user = self.mapper.get_one(self.session, username=login_request.username)
        if not user or not user.is_active:
            self.logger.warning("认证失败：用户不存在或未激活 username=%s", login_request.username)
            raise AuthenticationException("用户名或密码错误")

        # 验证密码并自动升级哈希
        ok, new_hash = verify_and_upgrade(login_request.password, user.password_hash)
        if not ok:
            self.logger.warning("认证失败：密码错误 username=%s", login_request.username)
            raise AuthenticationException("用户名或密码错误")

        if new_hash is not None:
            # 透明升级哈希，提升安全性
            self.mapper.update(self.session, user.id, {"password_hash": new_hash})  # type: ignore
            self.logger.info("已升级用户密码哈希 username=%s", login_request.username)

        # 生成访问令牌
        payload = {"user_id": str(user.id), "username": user.username, "role": user.role}
        access_token = create_access_token(payload)

        # 组装用户信息
        user_info = UserInfoVO.model_validate(user)

        self.logger.info("用户登录成功 username=%s", login_request.username)
        return UserLoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_info=user_info,
        )

    def logout(self, token: str) -> None:
        """
        登出：撤销令牌（加入黑名单直到过期）
        """
        ok = revoke_token(token)
        if ok:
            self.logger.info("用户登出成功，令牌已撤销")
        else:
            self.logger.warning("用户登出失败，令牌无效或已过期")

    def admin_create_user(self, payload: JwtPayload, req: AdminCreateUserRequest) -> int:
        """
        管理员创建用户
        :param actor_id: 执行操作的管理员ID
        :param req: 用户创建请求
        :return: 创建的用户ID
        """
        if payload.role != "admin":
            self.logger.warning("管理员创建用户失败, actor_id=%d 不是管理员", payload.user_id)
            raise AuthenticationException("您没有权限执行此操作")

        # 创建用户
        user = User(**req.model_dump())
        user.password_hash = get_password_hash(req.password)
        self.mapper.create(self.session, user)
        return user.id
    
    def list_users(self, payload: JwtPayload, page: int = 1, page_size: int = 10) -> tuple[list[UserInfoVO], int]:
        """
        管理员查询所有用户信息
        :param actor_id: 执行操作的管理员ID
        :return: 用户信息列表
        """
        if payload.role != "admin":
            self.logger.warning("管理员查询所有用户信息失败, actor_id=%d 不是管理员", payload.user_id)
            raise AuthenticationException("您没有权限执行此操作")

        # 查询所有用户
        users = self.mapper.list_users_info(self.session, page, page_size)
        total = self.mapper.count(self.session, is_active=True)
        return users, total

    def get_user_by_id(self, payload: JwtPayload, user_id: int) -> UserInfoVO:
        """
        管理员查询指定用户信息
        :param actor_id: 执行操作的管理员ID
        :param user_id: 用户ID
        :return: 用户信息
        """
        if payload.role != "admin":
            self.logger.warning("管理员查询指定用户信息失败, actor_id=%d 不是管理员", payload.user_id)
            raise AuthenticationException("您没有权限执行此操作")

        # 查询用户
        user = self.mapper.get_user_info_by_id(self.session, user_id=user_id)
        return user


def get_user_service(session: Session = Depends(get_session), mapper: UserMapper = Depends(get_user_mapper)) -> UserService:
    """
    获取用户服务实例
    :param session: 数据库会话
    :return: UserService实例
    """
    service = UserService(session, mapper)
    return service
