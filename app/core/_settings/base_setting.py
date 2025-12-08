import os

from pydantic_settings import BaseSettings

# --- 基础配置类 (只定义共享部分) ---
class BaseAppSettings(BaseSettings):
    """
    所有配置类的基础类，只定义共享的 env_file。
    """
    model_config = {
        "env_file": f".env.{os.getenv("ENVIRONMENT", "development")}",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }