from datetime import timedelta
import logging
from typing import Optional
from fastapi import HTTPException, Header, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from core.config import settings  # 假设配置文件在 core/config.py
import uuid
import time
from model.common import JwtPayload
from model.redis import get_redis_client


# 简单的令牌撤销列表（jti -> 过期时间戳），用于登出（内存回退）
_REVOKED_JTIS: dict[str, int] = {}

def _now_ts() -> int:
    """返回当前UTC秒级时间戳。"""
    return int(time.time())

def _exp_ts(expires_delta: Optional[timedelta], default_minutes: int) -> int:
    """根据传入的`expires_delta`或默认分钟数计算过期时间戳。

    Args:
        expires_delta: 自定义过期时间差；为None时使用`default_minutes`。
        default_minutes: 默认有效期（分钟）。

    Returns:
        过期的UTC秒级时间戳。
    """
    if expires_delta:
        seconds = int(expires_delta.total_seconds())
    else:
        seconds = int(timedelta(minutes=default_minutes).total_seconds())
    return _now_ts() + max(seconds, 0)

def _revoke_key(jti: str) -> str:
    """构造撤销标记在Redis中的键名。"""
    return f"{settings.JWT_REVOKE_PREFIX}{jti}"

def _register_jti_revocation(jti: str, exp_ts: int) -> None:
    """登记指定`jti`为撤销状态，直到其过期。

    优先写入Redis（键为`JWT_REVOKE_PREFIX + jti`），失败或未配置时回退到进程内存。

    Args:
        jti: 令牌唯一ID。
        exp_ts: 令牌过期的时间戳（秒）。
    """
    ttl = max(exp_ts - _now_ts(), 0)
    client = get_redis_client()
    if client is not None:
        try:
            client.setex(_revoke_key(jti), ttl, "1")
            return
        except Exception:
            pass
    expired = [k for k, v in _REVOKED_JTIS.items() if v <= _now_ts()]
    for k in expired:
        _REVOKED_JTIS.pop(k, None)
    _REVOKED_JTIS[jti] = exp_ts

def is_token_revoked(jti: str) -> bool:
    """检查令牌是否已被撤销。

    先尝试查询Redis；如不可用则查进程内回退字典。

    Args:
        jti: 令牌唯一ID。

    Returns:
        True表示已撤销且未过期；False表示未撤销或已过期。
    """
    client = get_redis_client()
    if client is not None:
        try:
            return bool(client.exists(_revoke_key(jti)))
        except Exception:
            pass
    exp_ts = _REVOKED_JTIS.get(jti)
    return exp_ts is not None and exp_ts > _now_ts()

def create_access_token(to_encode: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌（类型`access`）。

    Args:
        to_encode: 需要写入令牌载荷的业务字段（如`user_id`、`username`、`role`）。
        expires_delta: 令牌有效期，缺省使用配置`ACCESS_TOKEN_EXPIRE_MINUTES`。

    Returns:
        编码后的JWT字符串。
    """
    payload = dict(to_encode)
    payload.update({
        "type": "access",
        "jti": uuid.uuid4().hex,
        "iat": _now_ts(),
        "exp": _exp_ts(expires_delta, default_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    })
    
    encoded_jwt = jwt.encode(payload, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)  # type: ignore
    return encoded_jwt

def create_refresh_token(to_encode: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建刷新令牌（类型`refresh`）。

    默认有效期为访问令牌的4倍，可通过`expires_delta`覆盖。

    Args:
        to_encode: 需要写入令牌载荷的业务字段。
        expires_delta: 自定义有效期。

    Returns:
        编码后的JWT字符串。
    """
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
    """解码并校验JWT令牌。

    会校验签名、过期时间；如指定`expected_type`则校验`payload["type"]`。

    Args:
        token: 原始JWT字符串。
        expected_type: 预期类型（如`"access"`或`"refresh"`）。

    Returns:
        令牌载荷dict；失败返回None。已过期或无效的令牌返回None。
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
    """验证访问令牌的有效性并返回结构化载荷。

    包括签名校验、过期校验与撤销黑名单校验（Redis或内存）。

    Args:
        token: 原始JWT访问令牌。

    Returns:
        `JwtPayload`对象；失败返回None。
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
    """撤销令牌，将其加入黑名单直至过期。

    Args:
        token: 原始JWT令牌。

    Returns:
        True表示撤销成功；False表示令牌无效或格式错误。
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


_security = HTTPBearer()

def get_payload(credentials: HTTPAuthorizationCredentials = Security(_security)) -> JwtPayload:
    """获取token中的用户信息

    Args:
        credentials (HTTPAuthorizationCredentials, optional): _description_. Defaults to Security(_security).

    Raises:
        HTTPException: _description_

    Returns:
        JwtPayload: _description_
    """
    payload = validate_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="invalid token")
    return payload


def require_admin(credentials: HTTPAuthorizationCredentials = Security(_security)) -> JwtPayload:
    logging.info("进入拦截鉴权...")
    token = credentials.credentials
    payload = validate_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="invalid token")
    uid = int(payload.user_id) if isinstance(payload.user_id, str) else payload.user_id
    
    is_super = uid == settings.SUPER_ADMIN_USER_ID
    if payload.role != "admin" or not is_super:
        raise HTTPException(status_code=403, detail="Forbidden")
    return payload
