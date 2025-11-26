from datetime import datetime
from typing import List

from pydantic import BaseModel, field_serializer


class PostSimpleBaseVO(BaseModel):
    """
    文章简单信息基类(含字段id, title, summary, author_name, tag_names, category_names)
    - 不涉及tag_ids, category_ids, 不用增删改, 仅做展示用途
    """
    id: int
    title: str
    summary: str | None = ''
    author_name: str
    tag_names: str | None = None
    category_names: str | None = None


class PostDetailBase(BaseModel):
    """
    文章较为详细的信息基类(需要详细信息的地方通用属性有: id, title, summary, author_name, tag_ids, category_ids, tag_names, category_names)
    """
    id: int
    title: str
    summary: str | None = ''
    author_name: str
    tag_ids: str | None = None
    category_ids: str | None = None
    tag_names: str | None = None
    category_names: str | None = None

    @field_serializer("category_ids")
    def serialize_category_ids(self, category_ids: str | None) -> List[int]:
        if category_ids is None:
            return []
        if category_ids.find(',') == -1:
            return [int(category_ids)]
        return [int(id) for id in category_ids.split(",")]
    
    @field_serializer("tag_ids")
    def serialize_tag_ids(self, tag_ids: str | None) -> List[int]:
        if tag_ids is None:
            return []
        if tag_ids.find(',') == -1:
            return [int(tag_ids)]
        return [int(id) for id in tag_ids.split(",")]

    @field_serializer("tag_names")
    def serialize_tag_names(self, tag_names: str | None) -> List[str]:
        if tag_names is None:
            return []
        return tag_names.split(",")
    
    @field_serializer("category_names")
    def serialize_category_names(self, category_names: str | None) -> List[str]:
        if category_names is None:
            return []
        return category_names.split(",")

class PostCardVO(PostSimpleBaseVO):
    """用户端前端卡片展示所需信息
        (tag_ids不需要, 没有点击tag跳转的功能, 只需要tag_names)
    """
    create_time: datetime
    update_time: datetime
    view_count: int
    like_count: int
    category_ids: str | None = None

    @field_serializer("category_ids")
    def serialize_category_ids(self, category_ids: str | None) -> List[int]:
        if category_ids is None:
            return []
        return [int(id) for id in category_ids.split(",")]

    class Config:
        from_attributes = True


class U_PostInfo(BaseModel):
    """用户端文章详情页的文章基本信息
    """
    id: int
    title: str
    author_name: str
    tag_names: str | None = None
    category_names: str | None = None
    create_time: datetime | None
    update_time: datetime | None
    view_count: int | None
    like_count: int | None
    category_ids: str | None = None

    @field_serializer("category_ids")
    def serialize_category_ids(self, category_ids: str | None) -> List[int]:
        if category_ids is None:
            return None
        if category_ids.find(',') == -1:
            return [int(category_ids)]
        return [int(id) for id in category_ids.split(",")]
    

class U_PostDetailVO(PostSimpleBaseVO):
    """用户端前端文章全文阅读页展示所需信息
        包含基础信息和正文, 同样支持分类跳转需要category_ids
    """
    content: str
    create_time: datetime
    update_time: datetime
    view_count: int
    like_count: int
    category_ids: str | None = None

    @field_serializer("category_ids")
    def serialize_category_ids(self, category_ids: str | None) -> List[int]:
        if category_ids is None:
            return None
        if category_ids.find(',') == -1:
            return [int(category_ids)]
        return [int(id) for id in category_ids.split(",")]

    model_config = {
        "from_attributes": True,
    }

class PostInfoWithPath(BaseModel):
    """
        查询文章详情的数据盛放类, 用于过渡到PostDetailVO
    """
    id: int
    title: str
    summary: str | None = None
    author_name: str
    tag_names: str | None = None
    category_names: str | None = None
    content_file_path: str
    tag_ids: str | None = None
    category_ids: str | None = None
    create_time: datetime | None = None
    update_time: datetime | None = None
    view_count: int | None = None
    like_count: int | None = None

    model_config = {
        "from_attributes": True,
    }

class PostTableVO(PostDetailBase):
    """管理员端前端表格展示所需信息
        涉及tag, category, status的修改, 全部需要包含
    """
    post_status: str| None = None
    create_time: datetime | None = None
    update_time: datetime | None = None
    
    model_config = {
        "from_attributes": True,
    }

class PostEditVO(PostDetailBase):
    """管理员端前端编辑所需信息
        包含点赞数, 阅读数, 时间, 状态以外的全部信息
    """
    content: str
    model_config = {
        "from_attributes": True,
    }

class PostBodyMeta(BaseModel):
    """正文文件元信息"""
    path: str
    size: int
    mime: str
    filename: str
