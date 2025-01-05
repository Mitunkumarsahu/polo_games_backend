from fastapi import APIRouter, Depends, HTTPException, Query
from src.models.admin import Admin
from src.schemas.admin import AdminResponse, AdminCreate
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.db import get_db

admin_router = APIRouter()

