from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from src.db import get_db
from src.models.marqueetextstatement import MarqueeTextStatementModel

marqueetext_router = APIRouter()

def find_lowest_available_id(db: Session) -> int:
    """
    Find the lowest available ID for a new text statement.
    Returns 1 if no statements exist, otherwise finds the first gap in the sequence.
    """
    try:
        existing_ids = [stmt.id for stmt in db.query(MarqueeTextStatementModel.id).order_by(MarqueeTextStatementModel.id).all()]
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while finding the lowest available ID.")

    if not existing_ids:
        return 1

    for i in range(len(existing_ids)):
        expected_id = i + 1
        if existing_ids[i] != expected_id:
            return expected_id

    return len(existing_ids) + 1

@marqueetext_router.post("/create-statement")
def create_statement(content: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    """
    Create a new text statement with the lowest available ID.
    """
    try:
        new_id = find_lowest_available_id(db)
        new_statement = MarqueeTextStatementModel(id=new_id, statement=content)
        db.add(new_statement)
        db.commit()
        return {"message": "Text statement created successfully.", "id": new_id}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while creating the statement.")

@marqueetext_router.get("/statements", response_model=List[dict])
def get_statements(db: Session = Depends(get_db)):
    """
    Retrieve all text statements.
    """
    try:
        statements = db.query(MarqueeTextStatementModel).all()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while retrieving statements.")

    if not statements:
        raise HTTPException(status_code=404, detail="No statements found.")

    return [{"id": stmt.id, "content": stmt.statement} for stmt in statements]

@marqueetext_router.get("/statements/{statement_id}", response_model=dict)
def get_statement(statement_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific text statement by ID.
    """
    try:
        statement = db.query(MarqueeTextStatementModel).filter(MarqueeTextStatementModel.id == statement_id).first()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while retrieving the statement.")

    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found.")

    return {"id": statement.id, "content": statement.statement}

@marqueetext_router.put("/update-statement/{statement_id}")
def update_statement(statement_id: int, new_content: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    """
    Update the content of an existing text statement.
    """
    try:
        statement = db.query(MarqueeTextStatementModel).filter(MarqueeTextStatementModel.id == statement_id).first()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while fetching the statement.")

    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found.")

    try:
        statement.statement = new_content
        db.commit()
        return {"message": "Text statement updated successfully."}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while updating the statement.")

@marqueetext_router.delete("/delete-statement/{statement_id}")
def delete_statement(statement_id: int, db: Session = Depends(get_db)):
    """
    Delete a text statement by ID.
    """
    try:
        statement = db.query(MarqueeTextStatementModel).filter(MarqueeTextStatementModel.id == statement_id).first()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while fetching the statement.")

    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found.")

    try:
        db.delete(statement)
        db.commit()
        return {"message": "Text statement deleted successfully."}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while deleting the statement.")
