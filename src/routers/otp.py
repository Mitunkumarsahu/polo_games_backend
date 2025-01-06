import random
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from twilio.rest import Client
from src.db import get_db
from src.models.otp import OTPModel
from src.models.superadmin import SuperAdmin
from src.models.admin import Admin
from src.models.user import User
from src.jwttoken import create_access_token

import os
from dotenv import load_dotenv
load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

otp_router = APIRouter()


twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


@otp_router.post("/send-otp")
def send_otp(phone_number: str, db: Session = Depends(get_db)):
    """
    Search for the phone number in superadmins, admins, and users tables, then send OTP.
    """
    user = None
    for model in [SuperAdmin, Admin, User]:
        user = db.query(model).filter(model.phone_number == phone_number).first()
        if user:
            break
    
    if not user:
        raise HTTPException(status_code=404, detail="Phone number not found in any user tables")

    otp = f"{random.randint(100000, 999999)}"
    print(f"Generated OTP: {otp}")
    existing_otp = db.query(OTPModel).filter(OTPModel.phone_number == phone_number).first()

    try:
        if existing_otp:
            existing_otp.otp = otp
            existing_otp.created_at = datetime.utcnow()
            existing_otp.expires_at = datetime.utcnow() + timedelta(minutes=5)
        else:
            new_otp = OTPModel(phone_number=phone_number, otp=otp)
            db.add(new_otp)

        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save OTP: {str(e)}")

    try:
        twilio_client.messages.create(
            body=f"Your OTP for logging in to Polo Games is: {otp}",
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return {"message": "OTP sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send SMS: {str(e)}")



@otp_router.post("/verify-otp")
def verify_otp(phone_number: str, otp: str, db: Session = Depends(get_db)):
    """
    Verify OTP and return user's details with role information.
    """
    otp_entry = db.query(OTPModel).filter(OTPModel.phone_number == phone_number).first()

    if not otp_entry:
        raise HTTPException(status_code=404, detail="Phone number not found")
    if otp_entry.otp != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    if otp_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP has expired")

    otp_entry.is_verified = True
    db.commit()

    user = None
    role = None
    for model, role_name in [(SuperAdmin, "Superadmin"), (Admin, "Admin"), (User, "User")]:
        user = db.query(model).filter(model.phone_number == phone_number).first()
        if user:
            role = role_name
            break

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    token_data = {
        "sub": user.phone_number,
        "name": user.name if role in ["Admin", "Superadmin"] else user.username,
        "role": role
    }

    access_token = create_access_token(data=token_data)

    response = {
        "message": "OTP verified successfully",
        "name": user.name if role in ["Admin", "Superadmin"] else user.username,
        "phone_number": user.phone_number,
        "role": role,
        "access_token": access_token
    }

    if role == "Admin":
        response["permissions"] = user.permissions

    return response
