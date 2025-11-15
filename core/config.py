from pydantic_settings import BaseSettings
from pathlib import Path



class Settings(BaseSettings):
    DATABASE_URL: str
    
    
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str
    # 超级管理员的id, 默认为1, 可在.env中修改
    SUPER_ADMIN_USER_ID: int = 1
    # 作者的id, 默认为1, 可在.env中修改
    AUTHOR_ID: int = 1
    AUTHOR_NAME: str = "cattle"
    ENV: str = "dev"

    PROJECT_DIR: Path = Path(__file__).parent.parent
    # 博客正文存储目录（绝对路径）
    BLOG_STORAGE_DIR: Path = Path(__file__).parent.parent / "resources" / "blogs"
    AVATAR_STORAGE_DIR: Path = Path(__file__).parent.parent / "resources" / "avatar"

    LOG_LEVEL: str = "INFO"
    LOG_STACK_FRAMES: int = 6
    LOG_DIR: Path | None = None
    # Redis 配置（可选）
    REDIS_URL: str | None = None
    JWT_REVOKE_PREFIX: str = "revoked:jwt:"
    SENSITIVE_WORDS: list[str] = ["你妈死了"]

    class Config:
        env_file = ".env"

settings = Settings() # type: ignore
