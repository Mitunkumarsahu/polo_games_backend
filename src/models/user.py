from sqlalchemy import *
from datetime import datetime
from src.db import Base

class User(Base):
    __tablename__ = "Users"
    id = Column(INTEGER, primary_key=True, index=True, autoincrement=True, unique=True, nullable=False)
    username = Column(VARCHAR(255))
    country_code = Column(VARCHAR(255))
    phone_number = Column(VARCHAR(255), unique=True, nullable=False)
    selected_site = Column(VARCHAR(255))
    website_id = Column(VARCHAR(255), nullable=True)
    website_password = Column(VARCHAR(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)



