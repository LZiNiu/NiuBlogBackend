from pydantic import BaseModel


class CreateResponse(BaseModel):
    id: int
