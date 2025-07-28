from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from model.models import User
from model.user_api_models import UserResponse
from model.article_api_models import ArticleMeta
from services.user import get_all_user, get_user_by_id, get_user_by_name, get_article_meta_by_user_id
from model.db import get_session

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/create")
def create_new_user(user_name: str, pw: str, avatar: str = None):
    with next(get_session()) as session:
        user = User(username=user_name, password=pw, avatar=avatar)
        session.add(user)
        session.commit()
        session.refresh(user)
    return {"msg": "Successfully created"}


@router.get("/", response_model=list[UserResponse])
def list_all_user():
    return get_all_user()


@router.get("/{username}", response_model=list[UserResponse])
def get_single_user(username: str):
    user = get_user_by_name(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/getArticleMeta/{user_id}", response_model=list[ArticleMeta])
def get_user_article_meta(user_id: int):
    articles = get_article_meta_by_user_id(user_id)
    if not articles:
        raise HTTPException(status_code=404, detail="User not found")
    return articles
