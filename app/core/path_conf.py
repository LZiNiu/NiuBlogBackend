from pathlib import Path

BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

BLOG_DIR: Path = BASE_DIR / "resources" / "blogs"

AVATAR_DIR: Path = BASE_DIR / "resources" / "avatar"

DEFAULT_AVATAR_PATH: str = str(AVATAR_DIR / "default.jpg")

LOG_DIR: Path = BASE_DIR / "logs"