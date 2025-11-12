import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.user.UserController import user_router
from api.v1.admin.UserController import admin_router
from api.v1.auth.AuthController import auth_router
from handler.exception_handlers import register_exception_handlers
from core.config import settings
from core.lifespan import lifespan
import logging

app = FastAPI(lifespan=lifespan)

# 注册全局异常处理器
register_exception_handlers(app)

    # 创建自定义的日志记录器
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
app.include_router(user_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")



@app.get('/')
async def welcome() -> dict:
    return {"message": "Welcome to my Page!!"}



if __name__ == "__main__":
    uvicorn_error_logger = logging.getLogger("uvicorn.error")
    uvicorn_error_logger.disabled = True
    # uvicorn_default_logger = logging.getLogger("uvicorn")
    # uvicorn_default_logger.disabled = True
    uvicorn.run(app,host="127.0.0.1",port=8000)
    
    



