from pydantic import BaseModel

class TagDTO(BaseModel):
    name: str
    description: str | None = None