from argon2 import PasswordHasher
import argon2
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash

argon2.DEFAULT_MEMORY_COST
# 参数说明（可按实际硬件/安全需求调节）:
# RFC_9106_LOW_MEMORY默认参数
# - time_cost: 迭代次数（更高更慢更安全）3
# - memory_cost: 使用内存 KB（例如 64*1024 = 65536 KB = 64 MB）
# - parallelism: 并行线程数 4
# - hash_len: 输出哈希长度（字节） 32
# - salt_len: 盐长度（字节）16
pw_hasher = PasswordHasher()
class PasswordUtil:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        验证密码是否匹配。

        Args:
            plain_password (str): 明文密码
            hashed_password (str): 已哈希密码

        Returns:
            bool
        """
        try:
            pw_hasher.verify(hashed_password, plain_password)
            return True
        except VerifyMismatchError:
            return False
        except VerificationError:
            # 对未知/损坏的哈希返回 False（或按业务决定抛出）
            return False
        except InvalidHash:
            return False

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pw_hasher.hash(password)

    @staticmethod
    def needs_rehash(hashed_password: str) -> bool:
        """
        当变更参数（例如增加 memory_cost / time_cost)后,
        可以调用该方法判断是否需要用当前实例参数重新哈希已存密码。
        如果无法解析哈希InvalidHash, 返回 True表示需要重置/重新设置
        """
        try:
            return pw_hasher.check_needs_rehash(hashed_password)
        except InvalidHash:
            return True

    @staticmethod
    def verify_and_upgrade(plain_password: str, hashed_password: str) -> tuple[bool, str | None]:
        """
        验证密码是否匹配, 并在需要时重新哈希。

        Args:
            plain_password (str): 明文密码
            hashed_password (str): 已哈希密码

        Returns:
            tuple[bool, str | None]: (是否匹配, 新哈希密码或None)
        """
        ok = PasswordUtil.verify_password(plain_password, hashed_password)
        if not ok:
            return False, None
        if PasswordUtil.needs_rehash(hashed_password):
            return True, PasswordUtil.get_password_hash(plain_password)
        return True, None

