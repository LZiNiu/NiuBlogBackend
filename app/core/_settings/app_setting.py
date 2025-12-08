from .base_setting import BaseAppSettings

class AppSettings(BaseAppSettings):

    AUTHOR_ID: int = 1
    AUTHOR_NAME: str = "cattle"

    SENSITIVE_WORDS: list[str] = ["你妈死了"]
    SUPER_ADMIN_USER_ID: int = 1

    model_config = {
        **BaseAppSettings.model_config,
        "env_prefix": "APP_",   # 只读取 APP_ 开头
    }