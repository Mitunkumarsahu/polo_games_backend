from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db import get_db
from src.models.user import User
from src.schemas.user import CreateUser, UpdateUser

user_router = APIRouter()

@user_router.get("/get_all_users")
def index(db: Session = Depends(get_db)):
    return db.query(User).all()

@user_router.get("/get_user_by_id/{id}")
def get(id: int, db: Session = Depends(get_db)):
    return db.query(User).filter(User.id == id).first()

@user_router.post("/create_user")
def create(payload: CreateUser, db: Session = Depends(get_db)):
    user_instance = User(**payload.model_dump()) 
    db.add(user_instance)
    db.commit()
    db.refresh(user_instance) 
    return {"id": user_instance.id, "message": "User created successfully", "status": 201}

@user_router.put("/update_user_by_id/{id}")
def update(id: int, payload: UpdateUser, db: Session = Depends(get_db)):
    user_instance = db.query(User).filter(User.id == id).first()
    user_instance.username = payload.username
    user_instance.country_code = payload.country_code
    user_instance.phone_number = payload.phone_number
    user_instance.selected_site = payload.selected_site
    db.commit()
    db.refresh(user_instance)
    return {"id": user_instance.id, "message": "User data updated successfully", "status": 200}

@user_router.delete("/delete_user_by_phone_number/{phone_number}")
def delete(phone_number: str , db: Session = Depends(get_db)):
    db.query(User).filter(User.phone_number == phone_number).delete()
    db.commit()
    return {"message": "User deleted successfully", "status": 200}