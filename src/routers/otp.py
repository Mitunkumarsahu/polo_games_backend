import random
from typing import Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from src.db import get_db
from src.models.otp import OTPModel
from src.models.superadmin import SuperAdmin
from src.models.admin import Admin
from src.models.user import User
from src.jwttoken import create_access_token
import httpx

import os
from dotenv import load_dotenv
load_dotenv()


MSG91_AUTH_KEY = os.getenv("MSG91_AUTH_KEY")
MSG91_TEMPLATE_ID = os.getenv("MSG91_TEMPLATE_ID")
MSG91_BASE_URL = os.getenv("MSG91_BASE_URL")

otp_router = APIRouter()

@otp_router.post("/send-otp")
async def send_otp(phone_number: str, country_code: str, user_name: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Search for the phone number in superadmins, admins, and users tables, then send OTP.
    """
    user = None
    for model in [SuperAdmin, Admin, User]:
        user = db.query(model).filter(model.phone_number == phone_number, model.country_code == country_code).first()
        if user:
            break

    if not user:
        raise HTTPException(status_code=404, detail="Phone number not found in any user tables")
    

    otp = f"{random.randint(100000, 999999)}"
    print(f"Generated OTP: {otp}")

    existing_otp = db.query(OTPModel).filter(OTPModel.phone_number == phone_number, OTPModel.country_code == country_code).first()

    try:
        if existing_otp:
            existing_otp.otp = otp
            existing_otp.created_at = datetime.utcnow()
            existing_otp.expires_at = datetime.utcnow() + timedelta(minutes=5)
        else:
            new_otp = OTPModel(country_code=country_code, phone_number=phone_number, otp=otp)
            db.add(new_otp)

        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save OTP: {str(e)}")

    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "authkey": MSG91_AUTH_KEY,
                "accept": "application/json",
                "content-type": "application/json",
            }

            payload = {
                "template_id": MSG91_TEMPLATE_ID,
                "short_url": "1 (On) or 0 (Off)",
                "short_url_expiry": "Seconds (Optional)",
                "realTimeResponse": "1 (Optional)", 
                "recipients": [
                    {
                    "mobiles": f"{country_code}{phone_number}",
                    "var1": user_name,
                    "var2": otp
                    }
                ]
            }

            response = await client.post(MSG91_BASE_URL, json=payload, headers=headers)

            if response.status_code != 200:
                print(f"Response: {response.text}")
                raise HTTPException(status_code=500, detail="Failed to send SMS via MSG91")

            response_data = response.json()
            if response_data.get("type") != "success":
                raise HTTPException(status_code=500, detail="MSG91 API error")

            return {"message": "OTP sent successfully", "data": response_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send SMS: {str(e)}")


@otp_router.post("/verify-otp")
def verify_otp(phone_number: str, country_code: str, otp: str, db: Session = Depends(get_db)):
    """
    Verify OTP and return user's details with role information.
    """
    otp_entry = db.query(OTPModel).filter(OTPModel.phone_number == phone_number, OTPModel.country_code == country_code).first()

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
        "role": role,
    }

    access_token = create_access_token(data=token_data)

    response = {
        "message": "OTP verified successfully",
        "name": user.name if role in ["Admin", "Superadmin"] else user.username,
        "phone_number": user.phone_number,
        "role": role,
        "access_token": access_token,
    }

    if role == "Admin":
        response["permissions"] = user.permissions

    return response
