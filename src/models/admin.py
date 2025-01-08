from sqlalchemy import Column, Integer, String, JSON, DateTime
from datetime import datetime
from src.db import Base

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(15), unique=True, nullable=False)
    permissions = Column(
        JSON,
        default={
            "blog": {"read": True, "write": False, "delete": False},
            "reels": {"read": True, "write": False, "delete": False},
            "user": {"read": True, "write": False, "delete": False},
            "bannerimage": {"read": True, "write": False, "delete": False},
            "marqueetext": {"read": True, "write": False, "delete": False},
            "imagelink": {"read": True, "write": False, "delete": False},
            "offers": {"read": True, "write": False, "delete": False},
        },
    )
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


