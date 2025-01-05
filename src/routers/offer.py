from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from base64 import b64encode
from src.db import get_db
from src.models.offer import Offer
from src.schemas.offer import OfferCreate, OfferResponse
import base64
from datetime import datetime
from typing import List

offer_router = APIRouter()

def find_lowest_available_id(db: Session) -> int:
    """
    Find the lowest available ID for a new offer.
    """
    try:
        existing_ids = [offer.id for offer in db.query(Offer.id).order_by(Offer.id).all()]
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while finding the lowest available ID.")
    
    if not existing_ids:
        return 1

    for i in range(len(existing_ids)):
        expected_id = i + 1
        if existing_ids[i] != expected_id:
            return expected_id

    return len(existing_ids) + 1

@offer_router.get("/", response_model=List[OfferResponse])
def get_all_offers(db: Session = Depends(get_db)):
    """
    Retrieve all offers.
    """
    try:
        offers = db.query(Offer).all()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred.")
    
    if not offers:
        raise HTTPException(status_code=404, detail="No offers found.")
    return offers

@offer_router.get("/{offer_id}", response_model=OfferResponse)
def get_offer_by_id(offer_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific offer by ID.
    """
    try:
        offer = db.query(Offer).filter(Offer.id == offer_id).first()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred.")
    
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found.")
    return offer

# @offer_router.post("/create")
# def create_offer(
#     title: str,
#     description: str | None,
#     discount_percentage: float,
#     valid_from: datetime,
#     valid_until: datetime,
#     image: UploadFile = File(...),
#     db: Session = Depends(get_db),
# ):
#     try:
#         # Read and encode image
#         image_data = base64.b64encode(image.file.read()).decode("utf-8")
        
#         # Create offer instance
#         new_id = find_lowest_available_id(db)
#         new_offer = Offer(
#             id=new_id,
#             title=title,
#             description=description,
#             discount_percentage=discount_percentage,
#             valid_from=valid_from,
#             valid_until=valid_until,
#             image_base64=image_data,
#         )
#         db.add(new_offer)
#         db.commit()
#         db.refresh(new_offer)
#         return new_offer
#     except SQLAlchemyError as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# @offer_router.put("/{offer_id}", response_model=OfferResponse)
# async def update_offer(
#     offer_id: int,
#     title: str,
#     valid_from: str,
#     valid_until: str,
#     description: str = None,
#     discount_percentage: float = 0.0,
#     image: UploadFile = File(...),
#     db: Session = Depends(get_db),
# ):
#     """
#     Update an existing offer with a new base64-encoded image.
#     """
#     try:
#         offer = db.query(Offer).filter(Offer.id == offer_id).first()
#     except SQLAlchemyError:
#         raise HTTPException(status_code=500, detail="Database error occurred while fetching the offer.")
    
#     if not offer:
#         raise HTTPException(status_code=404, detail="Offer not found.")
    
#     try:
#         # Read and encode the new uploaded image
#         image_data = await image.read()
#         image_base64 = b64encode(image_data).decode("utf-8")

#         offer.title = title
#         offer.description = description
#         offer.discount_percentage = discount_percentage
#         offer.valid_from = valid_from
#         offer.valid_until = valid_until
#         offer.image_base64 = image_base64
        
#         db.commit()
#         db.refresh(offer)
#         return offer
#     except SQLAlchemyError:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="Database error occurred while updating the offer.")


@offer_router.post("/create", response_model=OfferResponse)
def create_offer(
    offer_data: OfferCreate = Depends(),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        # Read and encode the image in base64
        image_data = image.file.read()
        image_base64 = b64encode(image_data).decode("utf-8")
        
        # Create the offer instance
        new_id = find_lowest_available_id(db)
        new_offer = Offer(
            id=new_id,
            title=offer_data.title,
            description=offer_data.description,
            discount_percentage=offer_data.discount_percentage,
            valid_from=offer_data.valid_from,
            valid_until=offer_data.valid_until,
            image_base64=image_base64,
        )
        db.add(new_offer)
        db.commit()
        db.refresh(new_offer)
        return new_offer
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    


@offer_router.put("/{offer_id}", response_model=OfferResponse)
async def update_offer(
    offer_id: int,
    offer_data: OfferCreate = Depends(),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        offer = db.query(Offer).filter(Offer.id == offer_id).first()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while fetching the offer.")
    
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found.")
    
    try:
        # Read and encode the new uploaded image
        image_data = await image.read()
        image_base64 = b64encode(image_data).decode("utf-8")

        offer.title = offer_data.title
        offer.description = offer_data.description
        offer.discount_percentage = offer_data.discount_percentage
        offer.valid_from = offer_data.valid_from
        offer.valid_until = offer_data.valid_until
        offer.image_base64 = image_base64
        
        db.commit()
        db.refresh(offer)
        return offer
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while updating the offer.")
    except Exception as e:
        raise HTTPException(status_code=500, detail= f"An unexpected error occurred. error: {str(e)}")



@offer_router.delete("/{offer_id}")
def delete_offer(offer_id: int, db: Session = Depends(get_db)):
    """
    Delete an offer by ID.
    """
    try:
        offer = db.query(Offer).filter(Offer.id == offer_id).first()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while fetching the offer.")
    
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found.")
    
    try:
        db.delete(offer)
        db.commit()
        return {"message": "Offer deleted successfully."}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while deleting the offer.")
    except Exception as e:
        raise HTTPException(status_code=500, detail= f"An unexpected error occurred. error: {str(e)}")
