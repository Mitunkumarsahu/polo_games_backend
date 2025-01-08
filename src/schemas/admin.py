from pydantic import BaseModel
from typing import Dict

DEFAULT_PERMISSIONS = {
    "blog": {"read": True, "write": False, "delete": False},
    "reels": {"read": True, "write": False, "delete": False},
    "user": {"read": True, "write": False, "delete": False},
    "bannerimage": {"read": True, "write": False, "delete": False},
    "marqueetext": {"read": True, "write": False, "delete": False},
    "imagelink": {"read": True, "write": False, "delete": False},
    "offers": {"read": True, "write": False, "delete": False},
}

class AdminBase(BaseModel):
    phone_number: str
    name: str
    permissions: Dict[str, Dict[str, bool]] = DEFAULT_PERMISSIONS  

class AdminCreate(AdminBase):
    pass

class AdminResponse(AdminBase):
    id: int

    class Config:
        from_attributes = True


