from app.core._settings.base_setting import BaseAppSettings


class RedisSettings(BaseAppSettings):
    HOST: str = "localhost"
    PORT: int = 6379
    DB: int = 0
    PASSWORD: str | None = None
    POOL_SIZE: int = 8

    model_config = {
        **BaseAppSettings.model_config,
        "env_prefix": "REDIS_",
    }