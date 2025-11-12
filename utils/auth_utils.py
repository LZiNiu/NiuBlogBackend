from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException
import jwt

from core.config import settings  # 假设配置文件在 core/config.py
import uuid
import time
from model.common import JwtPayload
from model.redis import get_redis_client


# 简单的令牌撤销列表（jti -> 过期时间戳），用于登出（内存回退）
_REVOKED_JTIS: dict[str, int] = {}

def _now_ts() -> int:
    return int(time.time())

def _exp_ts(expires_delta: Optional[timedelta], default_minutes: int) -> int:
    if expires_delta:
        seconds = int(expires_delta.total_seconds())
    else:
        seconds = int(timedelta(minutes=default_minutes).total_seconds())
    return _now_ts() + max(seconds, 0)

def _revoke_key(jti: str) -> str:
    return f"{settings.JWT_REVOKE_PREFIX}{jti}"

def _register_jti_revocation(jti: str, exp_ts: int) -> None:
    # 优先使用全局 Redis 客户端；失败或未配置时回退到内存
    ttl = max(exp_ts - _now_ts(), 0)
    client = get_redis_client()
    if client is not None:
        try:
            client.setex(_revoke_key(jti), ttl, "1")
            return
        except Exception:
            pass
    # 清理内存已过期项并记录
    expired = [k for k, v in _REVOKED_JTIS.items() if v <= _now_ts()]
    for k in expired:
        _REVOKED_JTIS.pop(k, None)
    _REVOKED_JTIS[jti] = exp_ts

def is_token_revoked(jti: str) -> bool:
    """检查 jti 是否在撤销列表中且尚未过期"""
    client = get_redis_client()
    if client is not None:
        try:
            return bool(client.exists(_revoke_key(jti)))
        except Exception:
            pass
    exp_ts = _REVOKED_JTIS.get(jti)
    return exp_ts is not None and exp_ts > _now_ts()

def create_access_token(to_encode: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    payload = dict(to_encode)
    payload.update({
        "type": "access",
        "jti": uuid.uuid4().hex,
        "iat": _now_ts(),
        "exp": _exp_ts(expires_delta, default_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    })
    
    encoded_jwt = jwt.encode(payload, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)  # type: ignore
    return encoded_jwt

def create_refresh_token(to_encode: dict, expires_delta: Optional[timedelta] = None):
    """创建刷新令牌（有效期可更长，默认同 access）"""
    payload = dict(to_encode)
    # 默认刷新令牌有效期为访问令牌的 4 倍
    default_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 4
    payload.update({
        "type": "refresh",
        "jti": uuid.uuid4().hex,
        "iat": _now_ts(),
        "exp": _exp_ts(expires_delta, default_minutes=default_minutes),
    })
    encoded_jwt = jwt.encode(payload, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str, expected_type: Optional[str] = None) -> Optional[dict]:
    """
    解码并校验令牌基本有效性（签名+过期）；如指定 expected_type，则校验类型。
    返回 payload（dict），失败时返回 None。
    """
    try:
        payload: dict = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

    # # 校验类型
    # if expected_type and payload.get("type") != expected_type:
    #     return None

    # 校验过期
    exp = payload.get("exp")
    if not isinstance(exp, int):
        return None
    if exp <= _now_ts():
        return None

    return payload


def validate_access_token(token: str) -> Optional[JwtPayload]:
    """
    验证访问令牌：类型、过期与未撤销；返回 payload，失败返回 None。
    """
    payload = decode_token(token)
    if not payload:
        return None
    jti = payload.get("jti")
    if not isinstance(jti, str):
        return None
    if is_token_revoked(jti):
        return None
    return JwtPayload(**payload)

def revoke_token(token: str) -> bool:
    """
    撤销令牌（登出）：成功返回 True，失败返回 False。
    将令牌的 jti 加入撤销列表，过期后自动清理。
    """
    payload = decode_token(token)
    if not payload:
        return False
    jti = payload.get("jti")
    exp = payload.get("exp")
    if not isinstance(jti, str) or not isinstance(exp, int):
        return False
    _register_jti_revocation(jti, exp)
    return True


def get_token(authorization: str) -> str:
    """
    从请求头的Authorization中获取token令牌

    Args:
        authorization (str): 

    Returns:
        str: token令牌
    """
    if authorization.startswith("Bearer "):
        return authorization[len("Bearer "):].strip()
    return authorization.strip()

def get_payload(authorization: str) -> JwtPayload:
    """从请求头中获取token令牌并解析出其中携带的用户信息

    Args:
        authorization (str): 请求头参数

    Raises:
        HTTPException: 令牌无效错误

    Returns:
        JwtPayload: 用户信息
    """
    token = get_token(authorization)
    payload = validate_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="invalid token")
    return payload
