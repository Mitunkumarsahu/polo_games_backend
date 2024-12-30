from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from src.db import Base

class MarqueeTextStatementModel(Base):
    __tablename__ = "text_statements"

    id = Column(Integer, primary_key=True, index=True)
    statement = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
