from app.core._settings.base_setting import BaseAppSettings


class QiniuSettings(BaseAppSettings):
    ACCESS_KEY: str
    SECRET_KEY: str
    BUCKET_NAME: str
    DOMAIN: str
    
    model_config = {
        **BaseAppSettings.model_config,
        "env_prefix": "QINIU_",
    }
