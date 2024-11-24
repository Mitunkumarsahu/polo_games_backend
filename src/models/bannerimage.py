from sqlalchemy import Column, Integer, String, LargeBinary
from src.db import Base

class ImageModel(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    content = Column(LargeBinary, nullable=False)
    content_type = Column(String(50), nullable=False)