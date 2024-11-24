from pydantic import BaseModel
from decimal import Decimal

class CreateUser(BaseModel):
    username: str
    country_code: str
    phone_number: str
    selected_site: str

class UpdateUser(CreateUser):
    pass