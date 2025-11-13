from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from model.common import Base

# ==================== 枚举定义 ====================

class PostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class CommentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    SPAM = "spam"
    REJECTED = "rejected"


# ==================== 表模型 ====================

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    nickname: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, default="./resource/avatar/default.jpg")
    bio: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="user")
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<User id={getattr(self, 'id', None)} username={self.username}>"


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=func.now(), onupdate=func.now())


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=func.now(), onupdate=func.now())


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cover_image_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    content_file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, nullable=False)  # 逻辑外键
    status: Mapped[PostStatus] = mapped_column(String(20), default=PostStatus.DRAFT, nullable=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    like_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=False), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=func.now(), onupdate=func.now())


# 关联表
class PostCategory(Base):
    __tablename__ = "post_categories"

    post_id: Mapped[int] = mapped_column(Integer, primary_key=True)  # 逻辑外键
    category_id: Mapped[int] = mapped_column(Integer, primary_key=True)  # 逻辑外键


# 关联表
class PostTag(Base):
    __tablename__ = "post_tags"

    post_id: Mapped[int] = mapped_column(Integer, primary_key=True)  # 逻辑外键
    tag_id: Mapped[int] = mapped_column(Integer, primary_key=True)  # 逻辑外键


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(Integer, nullable=False)  # 逻辑外键
    author_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 逻辑外键
    author_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    author_email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 逻辑外键
    status: Mapped[CommentStatus] = mapped_column(String(20), default=CommentStatus.PENDING, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=func.now(), onupdate=func.now())


class Like(Base):
    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(Integer, nullable=False)  # 逻辑外键
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 逻辑外键
    visitor_identifier: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=func.now())