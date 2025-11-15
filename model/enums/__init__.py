from enum import Enum
# ==================== 枚举定义 ====================

class PostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class CommentStatus(str, Enum):
    PROCESSING = "processing"
    APPROVED = "approved"
    REJECTED = "rejected"

class Role(str, Enum):
    USER = "R_USER"
    ADMIN = "R_ADMIN"
    SUPER = "R_SUPER"
