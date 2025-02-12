from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class OfferBase(BaseModel):
    title: str
    description: str | None
    discount_percentage: float
    valid_from: datetime = Field(..., description="Format: YYYY-MM-DD")
    valid_until: datetime = Field(..., description="Format: YYYY-MM-DD")

class OfferCreate(OfferBase):
    pass
    # image: Optional[bytes]  

class OfferResponse(OfferBase):
    id: int
    image_base64: str 

    class Config:
        from_attributes = True




class VisibilityUpdateRequest(BaseModel):
    visible: bool