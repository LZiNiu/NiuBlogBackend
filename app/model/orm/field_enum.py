from enum import Enum
# ==================== 枚举定义 ====================

class PostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class Role(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    SUPER = "SUPER"

class TimelineEvent(str, Enum):
    coding = "coding"
    blog = "blog"
    life = "life"
    milestone = "milestone"
