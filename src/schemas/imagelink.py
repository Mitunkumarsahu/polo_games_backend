from pydantic import BaseModel

class ImageLinkResponse(BaseModel):
    id: int
    link: str
    image_base64: str  

    class Config:
        from_attribute = True  
