class BizCode:
    SUCCESS = 200
    ERROR = 500
    TOKEN_EXPIRED = 40101
    TOKEN_INVALID = 40102
    TOKEN_REVOKED = 40103
    TOKEN_REQUIRED = 40104
    FORBIDDEN = 40300
    VALIDATION_ERROR = 42200
    USER_NOT_FOUND = 40401
    ARTICLE_NOT_FOUND = 40402

class BizMsg:
    SUCCESS = "success"
    ERROR = "error"
    TOKEN_EXPIRED = "access token expired"
    TOKEN_INVALID = "invalid token"
    TOKEN_REVOKED = "token revoked"
    TOKEN_REQUIRED = "token required"
    FORBIDDEN = "Forbidden"
    VALIDATION_ERROR = "validation failed"
    DB_RECORD_NOT_FOUND = "数据库记录未找到, 请联系管理员确认id是否正确"
    USER_NOT_FOUND = "用户未找到"
    ARTICLE_NOT_FOUND = "文章未找到"