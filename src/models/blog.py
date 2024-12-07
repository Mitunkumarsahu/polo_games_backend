from sqlalchemy import Column, Integer, String, Text
from src.db import Base

class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text, nullable=False)
    author = Column(String, index=True)
