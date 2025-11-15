from pydantic import BaseModel


class TagVO(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
