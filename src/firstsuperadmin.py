from datetime import datetime
from sqlalchemy.orm import Session
from src.db import SessionLocal
from src.models.superadmin import SuperAdmin

import os
from dotenv import load_dotenv
load_dotenv()

FIRST_SUPERADMIN_PHONENUMBER = os.getenv("FIRST_SUPERADMIN_PHONENUMBER")
FIRST_SUPERADMIN_NAME = os.getenv("FIRST_SUPERADMIN_NAME")
FIRST_SUPERADMIN_COUNTRY_CODE = os.getenv("FIRST_SUPERADMIN_COUNTRY_CODE")


def create_first_superadmin():
    """
    Creates the first superadmin if it doesn't already exist.
    """
    db: Session = SessionLocal()
    try:
        existing_superadmin = db.query(SuperAdmin).first()
        if existing_superadmin:
            print("SuperAdmin already exists. Skipping creation.")
            return
        
        # superadmin = SuperAdmin(
        #     country_code=FIRST_SUPERADMIN_COUNTRY_CODE,
        #     phone_number=FIRST_SUPERADMIN_PHONENUMBER,  
        #     name=FIRST_SUPERADMIN_NAME, 
        #     created_at=datetime.utcnow()
        # )

        superadmin = SuperAdmin(
            country_code="91",
            phone_number="9333333330",
            name="Hardy",
            created_at=datetime.utcnow()
        )
        db.add(superadmin)
        db.commit()
        print("First SuperAdmin created successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error creating SuperAdmin: {e}")
    finally:
        db.close()
