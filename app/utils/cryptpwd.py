from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

class PasswordUtil:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def needs_rehash(hashed_password: str) -> bool:
        return pwd_context.needs_update(hashed_password)

    @staticmethod
    def verify_and_upgrade(plain_password: str, hashed_password: str) -> tuple[bool, str | None]:
        ok = PasswordUtil.verify_password(plain_password, hashed_password)
        if not ok:
            return False, None
        if PasswordUtil.needs_rehash(hashed_password):
            return True, PasswordUtil.get_password_hash(plain_password)
        return True, None

    @staticmethod
    def identify_scheme(hashed_password: str) -> str | None:
        info = pwd_context.identify(hashed_password)
        return info or None

# 兼容原有函数调用
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return PasswordUtil.verify_password(plain_password, hashed_password)
