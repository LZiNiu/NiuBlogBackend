from enum import Enum
# ==================== 枚举定义 ====================

class PostStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class CommentStatus(Enum):
    PROCESSING = "processing"
    APPROVED = "approved"
    REJECTED = "rejected"

class Role(Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    SUPER = "SUPER"
