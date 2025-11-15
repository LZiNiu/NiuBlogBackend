from pydantic_settings import BaseSettings, SettingsConfigDict

class JWTSettings(BaseSettings):
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str
    JWT_REVOKE_PREFIX: str = "revoked:jwt:"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="JWT_",   # 只读取 JWT_
        extra="ignore",
    )