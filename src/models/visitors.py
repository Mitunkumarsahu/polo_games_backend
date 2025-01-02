from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from src.db import Base

class Visitor(Base):
    __tablename__ = "visitors"
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, index=True)
    user_agent = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
