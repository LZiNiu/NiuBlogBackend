from app.core._settings.base_setting import BaseAppSettings
from pydantic import Field, computed_field
from urllib.parse import quote_plus


class DatabaseSettings(BaseAppSettings):
    TYPE: str = Field("mysql")
    HOST: str = Field("127.0.0.1")
    PORT: int = Field(3306)
    USER: str = Field("root", description="数据库用户名")
    PASSWORD: str = Field(..., description="数据库密码")
    NAME: str = Field(..., description="数据库名称")
    CHARSET: str = Field("utf8mb4", description="数据库编码")
    ECHO: bool = Field(False, description="是否打印 SQL")

    model_config = {
    **BaseAppSettings.model_config,
    "env_prefix": "DB_",  # 只读取 DB_
    }

    @computed_field
    @property
    def ASYNC_DB_URI(self) -> str:
        """获取异步数据库连接"""
        if self.TYPE == "mysql":
            # 推荐使用 asyncmy（SQLAlchemy 2 官方推荐）
            return f"mysql+asyncmy://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}?{self.CHARSET}"
        elif self.TYPE == "postgresql":
            # 使用 asyncpg（性能最佳）
            return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}?{self.CHARSET}"
        else:
            raise ValueError(f"Unsupported database type: {self.TYPE}")
