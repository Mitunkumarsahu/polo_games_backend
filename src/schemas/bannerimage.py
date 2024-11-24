from pydantic import BaseModel

class ImageResponse(BaseModel):
    message: str

    class Config:
        orm_mode = True
