from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseSettings):
    URL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DB_",  # 只读取 DB_
        extra="ignore",
    )