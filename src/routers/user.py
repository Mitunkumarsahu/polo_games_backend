from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.db import get_db
from src.models.user import User
from src.schemas.user import CreateUser, UpdateUser

user_router = APIRouter()

@user_router.get("/get_all_users")
def get_all_users(db: Session = Depends(get_db)):
    """
    Fetch all users from the database.
    """
    try:
        users = db.query(User).all()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while fetching all users.")
    if not users:
        raise HTTPException(status_code=404, detail="No users found.")
    return users

@user_router.get("/get_user_by_id/{id}")
def get_user_by_id(id: int, db: Session = Depends(get_db)):
    """
    Fetch a single user by their ID.
    """
    try:
        user = db.query(User).filter(User.id == id).first()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while fetching the user.")
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user

@user_router.post("/create_user")
def create_user(payload: CreateUser, db: Session = Depends(get_db)):
    """
    Create a new user in the database.
    """
    try:
        user_instance = User(**payload.model_dump())
        db.add(user_instance)
        db.commit()
        db.refresh(user_instance)
        return {"id": user_instance.id, "message": "User created successfully", "status": 201}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while creating the user.")

@user_router.put("/update_user_by_id/{id}")
def update_user_by_id(id: int, payload: UpdateUser, db: Session = Depends(get_db)):
    """
    Update an existing user by their ID.
    """
    try:
        user_instance = db.query(User).filter(User.id == id).first()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while updating the user.")
    
    if not user_instance:
            raise HTTPException(status_code=404, detail="User not found.")
    
    try:
        user_instance.username = payload.username
        user_instance.country_code = payload.country_code
        user_instance.phone_number = payload.phone_number
        user_instance.selected_site = payload.selected_site

        db.commit()
        db.refresh(user_instance)
        return {"id": user_instance.id, "message": "User data updated successfully", "status": 200}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while updating the user.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
    
    

@user_router.delete("/delete_user_by_phone_number/{phone_number}")
def delete_user_by_phone_number(phone_number: str, db: Session = Depends(get_db)):
    """
    Delete a user by their phone number.
    """
    try:
        user = db.query(User).filter(User.phone_number == phone_number).first()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while deleting the user.")
    
    if not user:
            raise HTTPException(status_code=404, detail="User not found.")
    
    try:
        db.delete(user)
        db.commit()
        return {"message": "User deleted successfully", "status": 200}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while deleting the user.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
    
