from fastapi import APIRouter

from .ArticleController import router as article_router
from .CategoryController import router as category_router
from .TagController import router as tag_router
from .CommonController import router as common_router
from .TimelineController import router as timeline_router


users_router = APIRouter(prefix="")
users_router.include_router(article_router)
users_router.include_router(category_router)
users_router.include_router(tag_router)
users_router.include_router(common_router)
users_router.include_router(timeline_router)
