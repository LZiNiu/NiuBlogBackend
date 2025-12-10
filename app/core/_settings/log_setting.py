from pathlib import Path
from typing import Literal, Dict
from pydantic import Field, computed_field
from app.core._settings.base_setting import BaseAppSettings
from app.core import path_conf


class LogSettings(BaseAppSettings):
    # --- 基础设置 ---
    level: str = Field(default="INFO", env="LOG_LEVEL")
    stack_trace_level: int = Field(default=8, env="LOG_STACK_TRACE_LEVEL")
    handler: Literal["console", "file", "both"] = Field(default="console", env="LOG_HANDLER")
    file_name: str = Field(default="app.log", env="LOG_FILE_NAME")
    file_max_size_mb: int = Field(default=10, env="LOG_FILE_MAX_SIZE_MB", description="日志文件最大大小 MB")
    file_backup_count: int = Field(default=5, env="LOG_FILE_BACKUP_COUNT", description="保留的日志文件备份数量")

    @computed_field
    @property
    def file_path(self) -> Path:
        return path_conf.LOG_DIR / Path(self.file_name)
    # --- 高级格式化设置 ---
    # 是否在日志中记录异常的完整堆栈信息
    exceptions: bool = Field(default=True, env="LOG_EXCEPTIONS")
    # 自定义日志格式字符串
    format: str = Field(
        default="%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s",
        env="LOG_FORMAT"
    )
    # 自定义日期格式字符串
    date_format: str = Field(
        default="%Y-%m-%d %H:%M:%S",
        env="LOG_DATE_FORMAT"
    )

    # --- 第三方库日志级别控制 ---
    # 允许覆盖特定模块的日志级别，例如 {"uvicorn.error": "INFO", "httpx": "WARNING"}
    # 这是一个高级功能，通过环境变量传入 JSON 字符串
    override_loggers: Dict[str, str] = Field(
        default_factory=dict,
        env="LOG_OVERRIDE_LOGGERS"
    )

    model_config = {
        **BaseAppSettings.model_config,
        "env_prefix": "LOG_",  # 只读取 LOG_
    }
