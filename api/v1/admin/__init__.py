from fastapi import APIRouter
from .UserController import router as user_router
from .ArticleController import router as article_router
from .CategoryController import router as category_router
from .TagController import router as tag_router
# from .CommentController import router as comment_router


admin_router = APIRouter(prefix="/admin")
admin_router.include_router(user_router)
admin_router.include_router(article_router)
admin_router.include_router(category_router)
admin_router.include_router(tag_router)
# admin_router.include_router(comment_router)