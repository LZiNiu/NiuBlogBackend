from pydantic import BaseModel


class UserResponse(BaseModel):
    username: str
    avatar: str | None

