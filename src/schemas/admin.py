from pydantic import BaseModel
from typing import Dict

class AdminBase(BaseModel):
    phone_number: str
    name: str
    permissions: Dict[str, bool]

class AdminCreate(AdminBase):
    pass

class AdminResponse(AdminBase):
    id: int

    class Config:
        from_attributes = True