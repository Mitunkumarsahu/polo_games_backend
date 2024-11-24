from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from base64 import b64encode
from sqlalchemy.orm import Session
from typing import List
from src.db import get_db
from src.models.bannerimage import ImageModel


image_router = APIRouter()

@image_router.post("/upload-images")
async def upload_images(
    files: List[UploadFile] = File(...), 
    db: Session = Depends(get_db)
):
    if len(files) != 3:
        raise HTTPException(
            status_code=400, detail="Exactly 3 images must be uploaded."
        )

    for file in files:
        if file.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type for {file.filename}. Only JPEG and PNG are allowed.",
            )

        content = await file.read()

        # Store in the database
        new_image = ImageModel(
            name=file.filename,
            content=content,
            content_type=file.content_type,
        )
        db.add(new_image)

    db.commit()
    return {"message": "Images uploaded successfully."}



@image_router.get("/images", response_model=list[dict])
def get_images(db: Session = Depends(get_db)):
    """
    API to retrieve all uploaded images with metadata and Base64 encoded content.
    """
    images = db.query(ImageModel).all()
    if not images:
        raise HTTPException(status_code=404, detail="No images found")
    
    response = []
    for img in images:
        base64_content = b64encode(img.content).decode("utf-8")
        response.append({
            "id": img.id,
            "name": img.name,
            "content_type": img.content_type,
            "content": f"data:{img.content_type};base64,{base64_content}"
        })
    
    return response


@image_router.get("/images/{image_id}", response_model=dict)
def get_image(image_id: int, db: Session = Depends(get_db)):
    """
    API to retrieve a specific image by ID with Base64 encoded content.
    """
    image = db.query(ImageModel).filter(ImageModel.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    base64_content = b64encode(image.content).decode("utf-8")
    return {
        "id": image.id,
        "name": image.name,
        "content_type": image.content_type,
        "content": f"data:{image.content_type};base64,{base64_content}"
    }