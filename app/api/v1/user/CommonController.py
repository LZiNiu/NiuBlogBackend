import asyncio
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.model import Result
from app.repository import (
    CategoryMapper,
    PostMapper,
    TagMapper,
    get_category_mapper,
    get_post_mapper,
    get_tag_mapper,
)
from app.db.session import get_session, AsyncSession
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="", tags=["综合信息接口"])

class ProfileInfo(BaseModel):
    category_count: int
    tag_count: int
    post_count: int

@router.get("/profile", response_model=Result[ProfileInfo])
async def get_profile_info(category_mapper: CategoryMapper = Depends(get_category_mapper),
                            tag_mapper: TagMapper = Depends(get_tag_mapper),
                            post_mapper: PostMapper = Depends(get_post_mapper),
                            db_session: AsyncSession = Depends(get_session)):
    try:
        category_count = await category_mapper.count(db_session)
        tag_count = await tag_mapper.count(db_session)
        post_count = await post_mapper.count(db_session)
    except RuntimeError as e:
        logger.error(f"获取综合信息失败: {e}")
        return Result.failure("获取综合信息失败", code=500)
    return Result.success(ProfileInfo(category_count=category_count, tag_count=tag_count, post_count=post_count))
