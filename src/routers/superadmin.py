from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.models.admin import Admin
from src.schemas.admin import AdminResponse, AdminCreate
from src.db import get_db
from sqlalchemy.exc import IntegrityError


superadmin_router = APIRouter()


def find_lowest_available_id(db: Session) -> int:
    """
    Find the lowest available ID for a new admin.
    Returns 1 if no admins exist, otherwise finds the first gap in the sequence.
    """
    try:
        existing_ids = [admin.id for admin in db.query(Admin.id).order_by(Admin.id).all()]
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while finding the lowest available ID.")

    if not existing_ids:
        return 1

    for i in range(len(existing_ids)):
        expected_id = i + 1
        if existing_ids[i] != expected_id:
            return expected_id

    return len(existing_ids) + 1

@superadmin_router.get("/", response_model=list[AdminResponse])
def read_admins(db: Session = Depends(get_db)):
    """
    Retrieve all admins from the database.
    """
    try:
        admins = db.query(Admin).all()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred.")
    if not admins:
        raise HTTPException(status_code=404, detail="No admins found.")
    return admins

@superadmin_router.get("/{admin_id}", response_model=AdminResponse)
def read_admin(admin_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific admin by ID.
    """
    try:
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred.")
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found.")
    return admin


@superadmin_router.post("/create_admins", response_model=AdminResponse)
def create_new_admin(admin: AdminCreate, db: Session = Depends(get_db)):
    try:
        new_id = find_lowest_available_id(db)
        new_admin = Admin(
            id=new_id,
            phone_number=admin.phone_number,
            name=admin.name,  
            permissions=admin.permissions,
        )
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)  
        return new_admin
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Phone number already exists.")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error occurred: {str(e)}")


    
@superadmin_router.delete("/{admin_id}")
def delete_admin(admin_id: int, db: Session = Depends(get_db)):
    """
    Delete an admin by ID.
    """
    try:
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found.")
        db.delete(admin)
        db.commit()
        return {"message": "Admin deleted successfully."}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while deleting the admin.")
    
@superadmin_router.put("/{admin_id}")
def update_existing_admin(admin_id: int, updated_admin: AdminCreate, db: Session = Depends(get_db)):
    """
    Update an existing admin by ID.
    """
    try:
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while fetching the admin.")
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found.")

    try:
        admin.name = updated_admin.name
        admin.phone_number = updated_admin.phone_number
        admin.permissions = updated_admin.permissions

        db.commit()
        return {"message": "Admin updated successfully.", "id": admin_id}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while updating the admin.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    



