from pydantic import BaseModel

class BatchDelete(BaseModel):
    ids: list[int]
