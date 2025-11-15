from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogSettings(BaseSettings):
    LEVEL: str = "INFO"
    STACK_FRAMES: int = 6
    DIR: str | Path |None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="LOG_",  # 只读取 LOG_
        extra="ignore",
    )
