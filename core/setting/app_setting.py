from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    ENV: str = "dev"
    AUTHOR_ID: int = 1
    AUTHOR_NAME: str = "cattle"

    PROJECT_DIR: Path = Path(__file__).resolve().parent.parent.parent
    BLOG_STORAGE_DIR: Path = PROJECT_DIR / "resources" / "blogs"
    AVATAR_STORAGE_DIR: Path = PROJECT_DIR / "resources" / "avatar"
    SENSITIVE_WORDS: list[str] = ["你妈死了"]
    SUPER_ADMIN_USER_ID: int = 1

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",   # 只读取 APP_ 开头
        extra="ignore"
    )