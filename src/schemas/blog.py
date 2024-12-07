from pydantic import BaseModel

class BlogBase(BaseModel):
    title: str
    content: str
    author: str

class BlogCreate(BlogBase):
    pass

class BlogResponse(BlogBase):
    id: int

    class Config:
        from_attributes = True
