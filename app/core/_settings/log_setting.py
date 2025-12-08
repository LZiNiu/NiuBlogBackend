from pathlib import Path

from app.core._settings.base_setting import BaseAppSettings


class LogSettings(BaseAppSettings):
    LEVEL: str = "INFO"
    STACK_FRAMES: int = 12

    model_config = {
        **BaseAppSettings.model_config,
        "env_prefix": "LOG_",  # 只读取 LOG_
    }
