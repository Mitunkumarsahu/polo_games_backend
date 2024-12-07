from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime, timedelta
from src.db import Base


class OTPModel(Base):
    __tablename__ = "otps"
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(15), nullable=False, unique=True)
    otp = Column(String(6), nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=5))
