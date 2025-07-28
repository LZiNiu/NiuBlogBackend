from fastapi import FastAPI
from api.v1 import article, user
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from model.db import SQLModel, engine
from services.user import create_user
from services.article import update_content_test, create_new_article

app = FastAPI()

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
app.include_router(article.router, prefix="/api/v1")
app.include_router(user.router, prefix="/api/v1")


@app.get('/')
async def welcome() -> dict:
    return {"message": "Welcome to my Page!!"}

# SQLModel.metadata.create_all(engine)
# create_user(user_name="admin", pw="123456")
# create_user(user_name="小明", pw="123456")
# create_user(user_name="小亮", pw="123456")

# create_new_article(article_title="测试文章1", content="# 标题1 如何使用fastapi", author_id=1, is_large_text=False)

# update_content_test()

# if __name__ == "__main__":
# 	uvicorn.run(app, host="127.0.0.1", port=8000)
