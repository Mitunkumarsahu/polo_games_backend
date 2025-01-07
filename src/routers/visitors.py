from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.models.visitors import Visitor
from src.db import get_db

visitor_router = APIRouter()

@visitor_router.post("/log-visitor")
async def log_visitor(request: Request, db: Session = Depends(get_db)):
    """
    Log visitor details (IP address and user-agent) into the database.
    """
    try:
        client_host = request.client.host
        user_agent = request.headers.get("user-agent")

        existing_visitor = db.query(Visitor).filter(
            Visitor.ip_address == client_host,
            Visitor.user_agent == user_agent
        ).first()

        if existing_visitor:
            return {"message": "Visitor already logged"}
        
        
        visitor = Visitor(ip_address=client_host, user_agent=user_agent)
        db.add(visitor)
        db.commit()
        return {"message": "Visitor logged"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while logging the visitor.")
    


@visitor_router.get("/visitor-count")
def get_visitor_count(db: Session = Depends(get_db)):
    """
    Retrieve the total number of visitors from the database.
    """
    try:
        count = db.query(Visitor).count()
        return {"count": count}
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while retrieving the visitor count.")
