from pydantic import BaseModel

class ImageResponse(BaseModel):
    message: str

    class Config:
        from_attributes = True
