from pydantic import Field
from pydantic_settings import BaseSettings

class QiniuSettings(BaseSettings):
    ACCESS_KEY: str = Field(..., env="QINIU_ACCESS_KEY")
    SECRET_KEY: str = Field(..., env="QINIU_SECRET_KEY")
    BUCKET_NAME: str = Field(..., env="QINIU_BUCKET_NAME")
    DOMAIN: str = Field(..., env="QINIU_DOMAIN")
    
    model_config = {
        "env_file": ".env",
        "env_prefix": "QINIU_",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }
