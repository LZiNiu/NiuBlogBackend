from pathlib import Path
from typing import Tuple, Optional
from fastapi import UploadFile
import tempfile
from qiniu import Auth, put_file_v2
from app.core import settings
from app.core import path_conf
import time
from app.utils.logger import get_logger
import shutil

_logger = get_logger(__name__)
# 本地存储
def _safe_name(name: str) -> str:
    p = Path(name)
    s = p.name
    return s.replace("\x00", "").strip()


# def save_avatar(file_bytes: bytes, filename: str, user_id: int) -> Tuple[Path, str]:
#     base = path_conf.AVATAR_STORAGE_DIR
#     target_dir = base / str(user_id)
#     target_dir.mkdir(parents=True, exist_ok=True)
#     safe = _safe_name(filename)
#     target = target_dir / safe
#     target.write_bytes(file_bytes)
#     rel = target.relative_to(base)
#     return target, str(rel)


def save_blog(file_bytes: bytes, filename: str) -> Tuple[Path, str]:
    base = path_conf.BLOG_DIR
    base.mkdir(parents=True, exist_ok=True)
    safe = _safe_name(filename)
    target = base / safe
    target.write_bytes(file_bytes)
    rel = target.relative_to(base)
    return target, str(rel)

# 七牛云存储


def upload_image_to_qiniu(file: UploadFile, upload_key: str) -> Tuple[Optional[str], Optional[str]]:
    """
    将前端发送的 multipart 图片文件上传到七牛云。

    Args:
        file (UploadFile): FastAPI 从请求中接收到的上传文件对象。

    Returns:
        Tuple[Optional[str], Optional[str]]:
            - 成功时返回 (图片访问 URL, None)
            - 失败时返回 (None, 错误信息描述)
    """
    # 1. 验证文件类型 (可选但推荐)
    allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if file.content_type not in allowed_types:
        return None, "仅支持 JPEG, PNG, GIF, WebP 格式的图片。"

    # 2. 生成上传到七牛云的唯一文件名
    original_filename = Path(file.filename)
    file_ext = original_filename.suffix
    key = f"{upload_key}/{int(time.time())}_{file.filename.replace(file_ext, '')}_{file_ext}"

    # 3. 创建临时文件来保存上传的文件内容
    with tempfile.NamedTemporaryFile(delete=False, dir=path_conf.AVATAR_DIR, suffix=file_ext) as temp_file:
        # 将上传的文件内容写入临时文件
        try:
            file.file.seek(0)
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path_str = temp_file.name
        except Exception as e:
            # 读取文件失败，清理临时文件
            Path(temp_file.name).unlink(missing_ok=True)
            return None, f"读取上传文件失败: {str(e)}"

    try:
        # 4. 使用七牛 SDK 上传临时文件
        # 构建鉴权对象
        q = Auth(settings.qiniu.ACCESS_KEY, settings.qiniu.SECRET_KEY)
        token = q.upload_token(settings.qiniu.BUCKET_NAME, key, expires=3600) # 设置 token 过期时间

        ret, info = put_file_v2(token, key, temp_file_path_str, version='v2')

        # 5. 检查上传结果
        if ret is not None and ret.get('key') == key:
            # 上传成功，返回访问 URL
            # 测试版本需要生成私有资源下载链接
            download_url = f"{settings.qiniu.DOMAIN.rstrip('/')}/{key}"
            # download_url = q.private_download_url(download_url)
            return download_url, None
        else:
            # 上传失败，info 对象包含了错误信息
            _logger.error(f"上传到七牛云失败: {info}. Error: {getattr(info, 'error', 'Unknown error')}")
            return None, f"上传到七牛云失败: {info}. Error: {getattr(info, 'error', 'Unknown error')}"
    except Exception as e:
        # 发生其他错误
        _logger.error(f"上传过程发生错误: {str(e)}")
        return None, f"上传过程发生错误: {str(e)}"
    finally:
        # 6. 无论成功与否，都要清理临时文件
        try:
            file.file.close()
            Path(temp_file_path_str).unlink(missing_ok=True)
        except OSError as e:
            _logger.error(f"清理临时文件失败: {e}") # 记录日志，但不中断流程


