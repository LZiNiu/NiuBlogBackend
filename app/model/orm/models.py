from datetime import datetime
from typing import Optional
from app.model.enums import PostStatus, Role
from sqlalchemy import DateTime, Integer, String, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.core import settings, path_conf
from app.model.common import Base

# ==================== 表模型 ====================

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    nickname: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, default=path_conf.DEFAULT_AVATAR_PATH)
    bio: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    role: Mapped[Role] = mapped_column(Enum(Role, values_callable=lambda t: [x.value for x in t]),
                                       nullable=False, default=Role.USER)
    is_active: Mapped[int] = mapped_column(Integer(), nullable=False, default=1, name="status")
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    create_time: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=func.now())
    update_time: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<User id={getattr(self, 'id', None)} username={self.username}>"


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    create_time: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=func.now())
    update_time: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=func.now(), onupdate=func.now())


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    create_time: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=func.now())
    update_time: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=func.now(), onupdate=func.now())


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cover_image_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    content_file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, nullable=False)
    author_name: Mapped[str] = mapped_column(String(15), nullable=False, default=settings.app.AUTHOR_NAME)
    post_status: Mapped[PostStatus] = mapped_column(Enum(PostStatus, values_callable=lambda t: [x.value for x in t]),
                                                    default=PostStatus.DRAFT, nullable=False, name="status")
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    like_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    create_time: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=func.now())
    update_time: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=func.now(), onupdate=func.now())


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



    
