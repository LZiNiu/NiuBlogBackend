from passlib.context import CryptContext

# 密码加密上下文
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

def needs_rehash(hashed_password: str) -> bool:
    """判断当前哈希是否需要升级（算法或参数变化时）"""
    return pwd_context.needs_update(hashed_password)

def verify_and_upgrade(plain_password: str, hashed_password: str) -> tuple[bool, str | None]:
    """
    验证密码；如验证成功且需要升级哈希，返回 (True, 新哈希)，否则返回 (True, None)。
    验证失败返回 (False, None)。
    """
    ok = verify_password(plain_password, hashed_password)
    if not ok:
        return False, None
    if needs_rehash(hashed_password):
        return True, get_password_hash(plain_password)
    return True, None

def identify_scheme(hashed_password: str) -> str | None:
    """识别哈希所使用的算法名称（如 'argon2', 'bcrypt'），无法识别返回 None"""
    info = pwd_context.identify(hashed_password)
    return info or None