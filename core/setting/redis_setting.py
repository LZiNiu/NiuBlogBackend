from pydantic_settings import BaseSettings, SettingsConfigDict

class RedisSettings(BaseSettings):
    HOST: str = "localhost"
    PORT: int = 6379
    DB: int = 0
    PASSWORD: str | None = None
    POOL_SIZE: int = 8

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="REDIS_",  # 只读取 REDIS_
        extra="ignore",
    )