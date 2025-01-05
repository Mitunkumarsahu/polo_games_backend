from sqlalchemy import Column, Integer, String, JSON, DateTime
from datetime import datetime
from src.db import Base

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(15), unique=True, nullable=False)
    permissions = Column(JSON, default={})  # Example: {"manage_users": True, "view_logs": False}
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
