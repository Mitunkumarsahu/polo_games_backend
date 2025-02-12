from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from src.db import Base
from datetime import datetime

class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    discount_percentage = Column(Float, nullable=False)
    valid_from = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime, nullable=False)
    image_base64 = Column(Text, nullable=False) 
    visible = Column(Integer, default=1)