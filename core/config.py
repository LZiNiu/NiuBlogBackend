from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    
    
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str

    LOG_LEVEL: str = "INFO"
    LOG_STACK_FRAMES: int = 6
    # Redis 配置（可选）
    REDIS_URL: str | None = None
    JWT_REVOKE_PREFIX: str = "revoked:jwt:"

    class Config:
        env_file = ".env"

settings = Settings() # type: ignore