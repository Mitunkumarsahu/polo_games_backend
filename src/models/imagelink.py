from sqlalchemy import Column, Integer, String, LargeBinary, DateTime
from sqlalchemy.sql import func
from src.db import Base

class ImageLink(Base):
    __tablename__ = "image_links"

    id = Column(Integer, primary_key=True, index=True)
    link = Column(String(255), nullable=False, unique=True)  
    image = Column(LargeBinary, nullable=False) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
