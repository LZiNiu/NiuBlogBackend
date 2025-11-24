from pydantic import BaseModel, ConfigDict

class PostCategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    post_id: int
    category_id: int
    order_index: int

class PostTagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    post_id: int
    tag_id: int
    order_index: int