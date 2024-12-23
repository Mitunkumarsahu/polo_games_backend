from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Query
from base64 import b64encode
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from src.db import get_db
from src.models.bannerimage import ImageModel

image_router = APIRouter()

def find_lowest_available_id(db: Session) -> int:
    """
    Find the lowest available ID for a new image.
    Returns 1 if no images exist, otherwise finds the first gap in the sequence.
    """
    try:
        existing_ids = [img.id for img in db.query(ImageModel.id).order_by(ImageModel.id).all()]
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while finding the lowest available ID.")

    if not existing_ids:
        return 1

    for i in range(len(existing_ids)):
        expected_id = i + 1
        if existing_ids[i] != expected_id:
            return expected_id

    return len(existing_ids) + 1

@image_router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    """
    Upload a single image to the database using the lowest available ID.
    """
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type for {file.filename}. Only JPEG and PNG are allowed.",
        )

    try:
        image_count = db.query(ImageModel).count()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while counting images.")

    if image_count >= 4:
        raise HTTPException(
            status_code=400, 
            detail="Image limit reached. You can store up to 4 images only."
        )

    try:
        content = await file.read()
        new_id = find_lowest_available_id(db)

        new_image = ImageModel(
            id=new_id,
            name=file.filename,
            content=content,
            content_type=file.content_type,
        )
        db.add(new_image)
        db.commit()

        return {"message": f"Image {file.filename} uploaded successfully with ID {new_id}."}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while uploading the image.")
    except Exception:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

@image_router.get("/images", response_model=List[dict])
def get_images(db: Session = Depends(get_db)):
    """
    API to retrieve all uploaded images with metadata and Base64 encoded content.
    """
    try:
        images = db.query(ImageModel).all()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while retrieving images.")

    if not images:
        raise HTTPException(status_code=404, detail="No images found.")

    response = [
        {
            "id": img.id,
            "name": img.name,
            "content_type": img.content_type,
            "content": f"data:{img.content_type};base64,{b64encode(img.content).decode('utf-8')}",
        }
        for img in images
    ]
    return response

@image_router.get("/images/{image_id}", response_model=dict)
def get_image(image_id: int, db: Session = Depends(get_db)):
    """
    API to retrieve a specific image by ID with Base64 encoded content.
    """
    try:
        image = db.query(ImageModel).filter(ImageModel.id == image_id).first()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while retrieving the image.")

    if not image:
        raise HTTPException(status_code=404, detail="Image not found.")

    return {
        "id": image.id,
        "name": image.name,
        "content_type": image.content_type,
        "content": f"data:{image.content_type};base64,{b64encode(image.content).decode('utf-8')}",
    }

@image_router.put("/update_image/{image_id}")
def update_image_name(image_id: int, new_name: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    """
    API to update the name of an existing image.
    """
    try:
        image = db.query(ImageModel).filter(ImageModel.id == image_id).first()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while fetching the image.")

    if not image:
        raise HTTPException(status_code=404, detail="Image not found.")

    try:
        image.name = new_name
        db.commit()
        return {"message": "Image name updated successfully."}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while updating the image.")

@image_router.delete("/delete_image/{image_id}")
def delete_image(image_id: int, db: Session = Depends(get_db)):
    """
    API to delete an image by ID.
    """
    try:
        image = db.query(ImageModel).filter(ImageModel.id == image_id).first()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while fetching the image.")

    if not image:
        raise HTTPException(status_code=404, detail="Image not found.")

    try:
        db.delete(image)
        db.commit()
        return {"message": "Image deleted successfully."}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while deleting the image.")
