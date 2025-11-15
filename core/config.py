from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path

from core.setting import (
    AppSettings,
    DatabaseSettings,
    JWTSettings,
    RedisSettings,
    LogSettings
)



class Settings:
    app: AppSettings
    jwt: JWTSettings
    redis: RedisSettings
    db: DatabaseSettings
    log: LogSettings

    def __init__(self):
        self.app = AppSettings()
        self.jwt = JWTSettings()
        self.redis = RedisSettings()
        self.db = DatabaseSettings()
        self.log = LogSettings()
        if self.log.DIR is None:
            self.log.DIR = self.app.PROJECT_DIR / "logs"
        else:
            self.log.DIR = self.app.PROJECT_DIR / self.log.DIR

settings = Settings()
