from pathlib import Path
from typing import Tuple

from core.config import settings


def _safe_name(name: str) -> str:
    p = Path(name)
    s = p.name
    return s.replace("\x00", "").strip()


def save_avatar(file_bytes: bytes, filename: str, user_id: int) -> Tuple[Path, str]:
    base = settings.AVATAR_STORAGE_DIR
    target_dir = base / str(user_id)
    target_dir.mkdir(parents=True, exist_ok=True)
    safe = _safe_name(filename)
    target = target_dir / safe
    target.write_bytes(file_bytes)
    rel = target.relative_to(base)
    return target, str(rel)


def save_blog(file_bytes: bytes, filename: str) -> Tuple[Path, str]:
    base = settings.BLOG_STORAGE_DIR
    base.mkdir(parents=True, exist_ok=True)
    safe = _safe_name(filename)
    target = base / safe
    target.write_bytes(file_bytes)
    rel = target.relative_to(base)
    return target, str(rel)
