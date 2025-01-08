from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from src.db import get_db
from src.models.superadmin import SuperAdmin
from src.models.admin import Admin
from src.models.user import User
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Decode the JWT token, validate it, and return the user along with their role.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone_number: str = payload.get("sub")
        if phone_number is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = None
        role = None
        for model, role_name in [(SuperAdmin, "Superadmin"), (Admin, "Admin"), (User, "User")]:
            user = db.query(model).filter(model.phone_number == phone_number).first()
            if user:
                role = role_name
                break

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return {"user": user, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    

def verify_role(required_roles: list):
    """
    Role-based access control decorator that accepts a list of roles.
    """
    def role_dependency(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in required_roles:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return current_user
    return role_dependency

# def verify_role(required_role: str):
#     """
#     Role-based access control decorator.
#     """
#     def role_dependency(current_user: dict = Depends(get_current_user)):
#         if current_user["role"] != required_role:
#             raise HTTPException(status_code=403, detail="Not enough permissions")
#         return current_user
#     return role_dependency
