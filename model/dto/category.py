from pydantic import BaseModel


class CategoryDTO(BaseModel):
    name: str
    description: str | None = None