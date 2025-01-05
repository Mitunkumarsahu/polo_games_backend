from datetime import datetime
from sqlalchemy.orm import Session
from src.db import SessionLocal
from src.models.superadmin import SuperAdmin



def create_first_superadmin():
    """
    Creates the first superadmin if it doesn't already exist.
    """
    db: Session = SessionLocal()
    try:
        # Check if a superadmin already exists
        existing_superadmin = db.query(SuperAdmin).first()
        if existing_superadmin:
            print("SuperAdmin already exists. Skipping creation.")
            return
        
        # Create a new superadmin
        superadmin = SuperAdmin(
            phone_number="1234567890",  
            name="First SuperAdmin", 
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
