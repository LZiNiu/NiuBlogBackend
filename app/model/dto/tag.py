from pydantic import BaseModel

class TagBase(BaseModel):
    name: str
    description: str | None = None

class TagCreate(TagBase):
    pass

class TagUpdate(TagBase):
    pass
