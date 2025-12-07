from fastapi import APIRouter

from .ArticleController import router as article_router
# from .UserController import router as blog_user_router
from .CategoryController import router as category_router
from .TagController import router as tag_router
# from .CommentController import router as comment_router


users_router = APIRouter(prefix="", tags=["用户端接口"])
users_router.include_router(article_router)
# users_router.include_router(blog_user_router)
users_router.include_router(category_router)
users_router.include_router(tag_router)
# users_router.include_router(comment_router)
