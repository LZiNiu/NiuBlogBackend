import time
from datetime import timedelta
from utils.jwt_utils import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    validate_access_token,
    revoke_token,
)

def test_access_token_issue_and_decode():
    payload = {"sub": "123", "username": "alice", "role": "user"}
    token = create_access_token(payload, expires_delta=timedelta(minutes=1))
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["type"] == "access"
    assert decoded["sub"] == "123"
    assert "jti" in decoded

def test_refresh_token_issue():
    payload = {"sub": "123", "username": "alice", "role": "user"}
    token = create_refresh_token(payload, expires_delta=timedelta(minutes=2))
    # 使用通用解码校验类型与过期
    # 不暴露 decode_refresh_token，统一使用 decode_token(expected_type="refresh")
    from utils.jwt_utils import decode_token
    decoded = decode_token(token, expected_type="refresh")
    assert decoded is not None
    assert decoded["type"] == "refresh"

def test_token_revoke_logout():
    payload = {"sub": "123"}
    token = create_access_token(payload, expires_delta=timedelta(minutes=1))
    # 未撤销时验证通过
    assert validate_access_token(token) is not None
    # 撤销令牌
    assert revoke_token(token) is True
    # 被撤销后验证失败
    assert validate_access_token(token) is None

def test_expired_token_invalid():
    payload = {"sub": "123"}
    # 直接生成过期令牌（过去 1 秒）
    token = create_access_token(payload, expires_delta=timedelta(seconds=-1))
    assert decode_access_token(token) is None
    assert validate_access_token(token) is None
