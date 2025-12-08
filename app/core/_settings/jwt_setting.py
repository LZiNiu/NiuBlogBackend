from app.core._settings.base_setting import BaseAppSettings


class JWTSettings(BaseAppSettings):
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str
    JWT_REVOKE_PREFIX: str = "revoked:jwt:"

    model_config = {
        **BaseAppSettings.model_config,
        "env_prefix": "JWT_",
    }