from datetime import timedelta
from typing import Optional
import jwt

from app.core import settings
import uuid
import time
from app.model import JwtPayload
from app.db.redis import get_redis
from app.utils.logger import get_logger

_REVOKED_JTIS: dict[str, int] = {}

def _now_ts() -> int:
    return int(time.time())

def _exp_ts(expires_delta: Optional[timedelta], default_minutes: int) -> int:
    """生成过期时间

    Args:
        expires_delta (Optional[timedelta]): 过期时间间隔，默认使用default_minutes
        default_minutes (int): 默认过期时间（分钟）

    Returns:
        int: 过期时间戳
    """
    if expires_delta:
        seconds = int(expires_delta.total_seconds())
    else:
        seconds = int(timedelta(minutes=default_minutes).total_seconds())
    return _now_ts() + max(seconds, 0)

def _revoke_key(jti: str) -> str:
    return f"{settings.jwt.JWT_REVOKE_PREFIX}{jti}"

async def _register_jti_revocation(jti: str, exp_ts: int) -> None:
    ttl = max(exp_ts - _now_ts(), 0)
    client = await get_redis()
    if client is not None:
        try:
            await client.setex(_revoke_key(jti), ttl, "1")
        except RuntimeError:
            expired = [k for k, v in _REVOKED_JTIS.items() if v <= _now_ts()]
            for k in expired:
                _REVOKED_JTIS.pop(k, None)
            _REVOKED_JTIS[jti] = exp_ts

async def is_token_revoked(jti: str) -> bool:
    start = time.perf_counter()
    client = await get_redis()
    end = time.perf_counter()
    JwtUtil.logger.debug(f"获取 Redis 客户端耗时: {end - start:.6f} 秒")
    if client is not None:
        try:
            revoked = bool(await client.exists(_revoke_key(jti)))
            return revoked
        except RuntimeError:
            JwtUtil.logger.error(f"redis操作失败")
            exp_ts = _REVOKED_JTIS.get(jti)
            return exp_ts is not None and exp_ts > _now_ts()

    raise ConnectionError("redis连接失败")


class JwtUtil:
    logger = get_logger(__name__)

    @staticmethod
    def create_access_token(to_encode: dict | JwtPayload, expires_delta: Optional[timedelta] = None) -> str:
        if isinstance(to_encode, JwtPayload):
            to_encode = to_encode.model_dump()
        payload = dict(to_encode)
        payload.update({
            "type": "access",       # 令牌类型：访问令牌，用于携带在业务请求的认证头
            "jti": uuid.uuid4().hex, # 令牌唯一ID：用于黑名单撤销与追踪
            "iat": _now_ts(),        # 签发时间：用于客户端与服务端的时间窗口校验
            "exp": _exp_ts(expires_delta, default_minutes=settings.jwt.ACCESS_TOKEN_EXPIRE_MINUTES), # 过期时间：服务端强制失效控制
        })
        return jwt.encode(payload, key=settings.jwt.SECRET_KEY, algorithm=settings.jwt.ALGORITHM)  # type: ignore

    @staticmethod
    def create_refresh_token(to_encode: dict | JwtPayload, expires_delta: Optional[timedelta] = None) -> str:
        if isinstance(to_encode, JwtPayload):
            to_encode = to_encode.model_dump()
        payload = dict(to_encode)
        default_minutes = settings.jwt.REFRESH_TOKEN_EXPIRE_MINUTES
        payload.update({
            "type": "refresh",      # 令牌类型：刷新令牌，仅用于获取新的访问令牌
            "jti": uuid.uuid4().hex, # 唯一ID：刷新令牌也可被撤销与轮换
            "iat": _now_ts(),        # 签发时间
            "exp": _exp_ts(expires_delta, default_minutes=default_minutes), # 默认刷新令牌时长的7天
        })
        return jwt.encode(payload, key=settings.jwt.SECRET_KEY, algorithm=settings.jwt.ALGORITHM)

    @staticmethod
    def decode_token(token: str, expected_type: Optional[str] = None) -> Optional[dict]:
        try:
            payload: dict = jwt.decode(
                token,
                settings.jwt.SECRET_KEY,
                algorithms=[settings.jwt.ALGORITHM],
            )
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        if expected_type and payload.get("type") != expected_type:
            return None
        exp = payload.get("exp")
        if not isinstance(exp, int):
            return None
        if exp <= _now_ts():
            return None
        return payload

    @staticmethod
    def decode_with_reason(token: str, expected_type: Optional[str] = None) -> tuple[Optional[dict], Optional[str]]:
        try:
            payload: dict = jwt.decode(
                token,
                settings.jwt.SECRET_KEY,
                algorithms=[settings.jwt.ALGORITHM],
            )
        except jwt.ExpiredSignatureError:
            return None, "expired"
        except jwt.InvalidTokenError:
            return None, "invalid"
        if expected_type and payload.get("type") != expected_type:
            return None, "invalid"
        exp = payload.get("exp")
        if not isinstance(exp, int):
            return None, "invalid"
        if exp <= _now_ts():
            return None, "expired"
        return payload, None

    @staticmethod
    def validate_access_token(token: str) -> Optional[JwtPayload]:
        payload = JwtUtil.decode_token(token, expected_type="access")
        if not payload:
            return None
        jti = payload.get("jti")
        if not isinstance(jti, str):
            return None
        if is_token_revoked(jti):
            return None
        return JwtPayload(**payload)

    @staticmethod
    def revoke_token(token: str) -> bool:
        payload = JwtUtil.decode_token(token)
        if not payload:
            return False
        jti = payload.get("jti")
        exp = payload.get("exp")
        if not isinstance(jti, str) or not isinstance(exp, int):
            return False
        _register_jti_revocation(jti, exp)
        return True

    @staticmethod
    def issue_token_pair(to_encode: dict | JwtPayload) -> tuple[str, str]:
        access = JwtUtil.create_access_token(to_encode)
        refresh = JwtUtil.create_refresh_token(to_encode)
        return access, refresh

    @staticmethod
    def refresh_token_pair(refresh_token: str) -> Optional[tuple[str, str]]:
        payload = JwtUtil.decode_token(refresh_token, expected_type="refresh")
        if not payload:
            return None
        JwtUtil.revoke_token(refresh_token)
        base = JwtPayload(**payload)
        return JwtUtil.issue_token_pair(base)

    @staticmethod
    async def get_payload(token: str) -> JwtPayload | None:
        # 解码令牌
        payload, reason = JwtUtil.decode_with_reason(token, expected_type="access")
        if reason:
            JwtUtil.logger.info(f"decode token {token} with reason {reason}")
        if not payload:
            return None
        jti = payload.get("jti")
        if isinstance(jti, str) and await is_token_revoked(jti):
            return None
        return JwtPayload(**payload)

