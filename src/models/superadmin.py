from sqlalchemy import Column, Integer, String, DateTime, VARCHAR
from datetime import datetime
from src.db import Base

class SuperAdmin(Base):
    __tablename__ = "superadmins"
    id = Column(Integer, primary_key=True, index=True)
    country_code = Column(VARCHAR(255))
    phone_number = Column(String(15), unique=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)