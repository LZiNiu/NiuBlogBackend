import time
from datetime import timedelta
from utils.auth_utils import JwtUtil

def test_access_token_issue_and_decode():
    payload = {"user_id": "123", "username": "alice", "role": "user"}
    token = JwtUtil.create_access_token(payload, expires_delta=timedelta(minutes=1))
    decoded = JwtUtil.decode_token(token)
    assert decoded is not None
    assert decoded["type"] == "access"
    assert decoded["user_id"] == "123"
    assert "jti" in decoded

def test_refresh_token_issue():
    payload = {"user_id": "123", "username": "alice", "role": "user"}
    token = JwtUtil.create_refresh_token(payload, expires_delta=timedelta(minutes=2))
    # 使用通用解码校验类型与过期
    # 不暴露 decode_refresh_token，统一使用 decode_token(expected_type="refresh")
    decoded = JwtUtil.decode_token(token, expected_type="refresh")
    assert decoded is not None
    assert decoded["type"] == "refresh"

def test_token_revoke_logout():
    payload = {"user_id": "123"}
    token = JwtUtil.create_access_token(payload, expires_delta=timedelta(minutes=1))
    # 未撤销时验证通过
    assert JwtUtil.validate_access_token(token) is not None
    # 撤销令牌
    assert JwtUtil.revoke_token(token) is True
    # 被撤销后验证失败
    assert JwtUtil.validate_access_token(token) is None

def test_expired_token_invalid():
    payload = {"user_id": "123"}
    # 直接生成过期令牌（过去 1 秒）
    token = JwtUtil.create_access_token(payload, expires_delta=timedelta(seconds=-1))
    assert JwtUtil.decode_token(token) is None
    assert JwtUtil.validate_access_token(token) is None
