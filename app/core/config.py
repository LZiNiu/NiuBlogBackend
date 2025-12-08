from pydantic import Field
from app.core._settings import (
    AppSettings,
    DatabaseSettings,
    JWTSettings,
    RedisSettings,
    LogSettings,
    QiniuSettings,
    BaseAppSettings
)



class Settings(BaseAppSettings):
    app: AppSettings = Field(default_factory=AppSettings)
    jwt: JWTSettings = Field(default_factory=JWTSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    log: LogSettings = Field(default_factory=LogSettings)
    qiniu: QiniuSettings = Field(default_factory=QiniuSettings)

settings = Settings()
