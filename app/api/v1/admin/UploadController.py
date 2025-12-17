from fastapi import APIRouter, Depends, File, UploadFile, status
from typing import TypedDict

from app.model import Result
from app.utils.upload import upload_image_to_qiniu


router = APIRouter(prefix="/upload", tags=["管理端上传接口"])


class UploadResponse(TypedDict):
    url: str

@router.post("/avatar", response_model=Result[UploadResponse])
def upload_avatar(file: UploadFile = File(...)):
    # 头像上传
    avatar_url, reason = upload_image_to_qiniu(file, "avatar")
    if not avatar_url:
        return Result.failure(msg=reason, code=status.HTTP_422_UNPROCESSABLE_CONTENT)
    return Result.success(UploadResponse(url=avatar_url))


@router.post("/illustration", response_model=Result[UploadResponse])
def upload_illustration(file: UploadFile = File(...)):
    # 插图上传
    illustration_url, reason = upload_image_to_qiniu(file, "illustration")
    if not illustration_url:
        return Result.failure(msg=reason, code=status.HTTP_422_UNPROCESSABLE_CONTENT)
    return Result.success(UploadResponse(url=illustration_url))


@router.post("/cover", response_model=Result[UploadResponse])
def upload_cover(file: UploadFile = File(...)):
    # 封面图上传
    cover_url, reason = upload_image_to_qiniu(file, "cover")
    if not cover_url:
        return Result.failure(msg=reason, code=status.HTTP_422_UNPROCESSABLE_CONTENT)
    return Result.success(UploadResponse(url=cover_url))
