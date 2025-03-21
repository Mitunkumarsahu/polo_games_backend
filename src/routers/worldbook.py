from fastapi import FastAPI, HTTPException, UploadFile, File, Form, APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from src.db import get_db
import base64
from src.models.worldbook import WorldBook
from src.schemas.imagelink import ImageLinkResponse
from src.auth_dependencies import verify_role

app = FastAPI()

world_book_router = APIRouter()

def image_to_binary(image: UploadFile) -> bytes:
    try:
        content = image.file.read()
        return content  
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading image: {e}")
    
def binary_to_base64(binary_data):
    return base64.b64encode(binary_data).decode("utf-8")

def find_lowest_available_id(db: Session) -> int:
    try:
        existing_ids = [entry.id for entry in db.query(WorldBook.id).order_by(WorldBook.id).all()]
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while finding the lowest available ID.")
    
    if not existing_ids:
        return 1

    for i in range(len(existing_ids)):
        expected_id = i + 1
        if existing_ids[i] != expected_id:
            return expected_id

    return len(existing_ids) + 1


@world_book_router.post("/create_items/", response_model=ImageLinkResponse)
def create_item(link: str = Form(...), image: UploadFile = File(...), db: Session = Depends(get_db), current_user: dict = Depends(verify_role(["Admin", "Superadmin"]))):
    try:
        image_data = image_to_binary(image)  
        new_id = find_lowest_available_id(db)
        new_item = WorldBook(id=new_id, link=link, image=image_data)  
        db.add(new_item)
        db.commit()
        db.refresh(new_item)

        image_base64 = base64.b64encode(image_data).decode('utf-8') 
        return ImageLinkResponse(id=new_item.id, link=new_item.link, image_base64=image_base64)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred while creating the item: {e}")

@world_book_router.get("/items/", response_model=List[ImageLinkResponse])
def read_items(db: Session = Depends(get_db)):
    try:
        items = db.query(WorldBook).all()
        response_items = []
        for item in items:
            image_base64 = base64.b64encode(item.image).decode('utf-8')  
            response_item = ImageLinkResponse(
                id=item.id,
                link=item.link,
                image_base64=image_base64
            )
            response_items.append(response_item)

        return response_items
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while reading items.")


@world_book_router.get("/items/{item_id}", response_model=ImageLinkResponse)
def read_item(item_id: int, db: Session = Depends(get_db)):
    try:
        item = db.query(WorldBook).filter(WorldBook.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found.")
        
        image_base64 = base64.b64encode(item.image).decode('utf-8')
        
        return ImageLinkResponse(
            id=item.id,
            link=item.link,
            image_base64=image_base64
        )
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while reading the item.")

@world_book_router.put("/items/{item_id}", response_model=ImageLinkResponse)
def update_item(item_id: int, link: str = Form(...), image: UploadFile = File(...), db: Session = Depends(get_db), current_user: dict = Depends(verify_role(["Admin", "Superadmin"]))):
    try:
        item = db.query(WorldBook).filter(WorldBook.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found.")
        
        image_data = image_to_binary(image)  
        
        item.link = link
        item.image = image_data  
        
        db.commit()
        db.refresh(item)

        image_base64 = binary_to_base64(item.image)

        return ImageLinkResponse(id=item.id, link=item.link, image_base64=image_base64)
    
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while updating the item.")

@world_book_router.delete("/items/{item_id}", response_model=dict)
def delete_item(item_id: int, db: Session = Depends(get_db), current_user: dict = Depends(verify_role(["Admin", "Superadmin"]))):
    try:
        item = db.query(WorldBook).filter(WorldBook.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found.")
        db.delete(item)
        db.commit()
        return {"message": "Item deleted successfully"}
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while deleting the item.")
