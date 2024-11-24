import random
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from twilio.rest import Client
from src.db import get_db
from src.models.otp import OTPModel

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
    API to send a 6-digit OTP via Twilio SMS to a given phone number.
    """
    otp = f"{random.randint(100000, 999999)}"
    
    existing_otp = db.query(OTPModel).filter(OTPModel.phone_number == phone_number).first()
    if existing_otp:
        existing_otp.otp = otp
        existing_otp.created_at = datetime.utcnow()
        existing_otp.expires_at = datetime.utcnow() + timedelta(minutes=5)
    else:
        new_otp = OTPModel(
            phone_number=phone_number,
            otp=otp
        )
        db.add(new_otp)
    
    db.commit()

    try:
        message = twilio_client.messages.create(
            body=f"Your OTP is: {otp}",
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )

        if message.error_code:
            raise HTTPException(status_code=400, detail=f"Failed to send SMS: {message.error_message}")
        
        return {"message": "OTP sent successfully", "phone_number": phone_number}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send SMS: {str(e)}")

    



@otp_router.post("/verify-otp")
def verify_otp(phone_number: str, otp: str, db: Session = Depends(get_db)):
    """
    API to verify the OTP sent to a phone number.
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

    return {"message": "OTP verified successfully", "phone_number": phone_number}
