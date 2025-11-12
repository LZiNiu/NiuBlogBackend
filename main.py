import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1 import UserController
from handler.exception_handlers import register_exception_handlers
from core.config import settings
from core.logger import setup_logging, get_log_config
from core.lifespan import lifespan

# 初始化彩色日志（浅堆栈）
setup_logging(level=settings.LOG_LEVEL, max_frames=settings.LOG_STACK_FRAMES)

app = FastAPI(lifespan=lifespan)

# 注册全局异常处理器
register_exception_handlers(app)
# origins = [
#     "http://localhost",
#     "http://localhost:8080",
#     "https://localhost",
#     "https://localhost:8080",
# ]
# 
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# app.include_router(ArticleController.router, prefix="/api/v1")
app.include_router(UserController.auth_router, prefix="/api/v1")


@app.get('/')
async def welcome() -> dict:
    return {"message": "Welcome to my Page!!"}

# SQLModel.metadata.create_all(engine)
# create_user(user_name="admin", pw="123456")
# create_user(user_name="小明", pw="123456")
# create_user(user_name="小亮", pw="123456")

# create_new_article(article_title="测试文章1", content="# 标题1 如何使用fastapi", author_id=1, is_large_text=False)

# update_content_test()

if __name__ == "__main__":
	uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level=settings.LOG_LEVEL.lower(),
        log_config=get_log_config(level=settings.LOG_LEVEL, max_frames=settings.LOG_STACK_FRAMES),
    )
