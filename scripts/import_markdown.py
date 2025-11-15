import sys
from pathlib import Path
sys.path.insert(0, str(Path("...").resolve()))
import asyncio

import re
from typing import Any, Dict, List, Optional, Tuple

from core.config import settings
from model.db import _ensure_engine
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from model.entity.models import Category, Tag, Post
from services.post import PostService, get_post_mapper, get_category_mapper, get_tag_mapper
from model.dto.post import PostCreateDTO



def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


async def _ensure_named_id(session: AsyncSession, model, name: str) -> int:
    result = await session.execute(select(model).where(model.name == name))
    obj = result.scalars().first()
    if obj:
        return obj.id  # type: ignore
    new = model(name=name)
    session.add(new)
    await session.flush()
    return new.id  # type: ignore


async def _import_one(session: AsyncSession, service: PostService, path: Path) -> Optional[int]:
    text = _read_text(path)
    title = text.splitlines()[0].lstrip("#").strip()
    # 空文件(想好了文件名但没写东西)
    if not title:
        title = path.stem
    summary = None

    base = settings.app.BLOG_STORAGE_DIR.resolve()
    try:
        rel = path.resolve().relative_to(base)
        rel_str = str(rel)
    except Exception:
        rel_str = path.name
    dto = PostCreateDTO(
        title=str(title),
        summary=summary,
        content_file_path=rel_str,
        status="draft",
    )
    post_id = await service.create_post(dto)
    return post_id


async def main() -> None:
    _ensure_engine()
    from model.db import SessionLocal
    async with SessionLocal() as session:
        service = PostService(session, get_post_mapper(), get_category_mapper(), get_tag_mapper())
        base = settings.app.BLOG_STORAGE_DIR.resolve()
        created: List[Tuple[int, str]] = []
        for p in base.rglob("*.md"):
            pid = await _import_one(session, service, p)
            if pid:
                created.append((pid, str(p)))
    if created:
        print("Imported posts:")
        for pid, p in created:
            print(f" - id={pid} file={p}")


if __name__ == "__main__":
    asyncio.run(main())
