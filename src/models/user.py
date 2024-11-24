from sqlalchemy import *
from src.db import Base

class User(Base):
    __tablename__ = "Users"
    id = Column(INTEGER, primary_key=True, index=True, autoincrement=True, unique=True, nullable=False)
    username = Column(VARCHAR(255))
    country_code = Column(VARCHAR(255))
    phone_number = Column(VARCHAR(255), unique=True, nullable=False)
    selected_site = Column(VARCHAR(255))
