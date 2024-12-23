from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.db import get_db
from src.models.blog import Blog
from src.schemas.blog import BlogCreate, BlogResponse

blog_router = APIRouter()

def find_lowest_available_id(db: Session) -> int:
    """
    Find the lowest available ID for a new blog.
    Returns 1 if no blogs exist, otherwise finds the first gap in the sequence.
    """
    try:
        existing_ids = [blog.id for blog in db.query(Blog.id).order_by(Blog.id).all()]
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while finding the lowest available ID.")

    if not existing_ids:
        return 1

    for i in range(len(existing_ids)):
        expected_id = i + 1
        if existing_ids[i] != expected_id:
            return expected_id

    return len(existing_ids) + 1

@blog_router.get("/", response_model=list[BlogResponse])
def read_blogs(db: Session = Depends(get_db)):
    """
    Retrieve all blogs from the database.
    """
    try:
        blogs = db.query(Blog).all()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred.")
    if not blogs:
        raise HTTPException(status_code=404, detail="No blogs found.")
    return blogs

@blog_router.get("/{blog_id}", response_model=BlogResponse)
def read_blog(blog_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific blog by ID.
    """
    try:
        blog = db.query(Blog).filter(Blog.id == blog_id).first()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred.")
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found.")
    return blog

@blog_router.post("/create_blogs", response_model=BlogResponse)
def create_new_blog(blog: BlogCreate, db: Session = Depends(get_db)):
    """
    Create a new blog entry using the lowest available ID.
    """
    try:
        new_id = find_lowest_available_id(db)
        new_blog = Blog(id=new_id, **blog.dict())
        db.add(new_blog)
        db.commit()
        db.refresh(new_blog)
        return new_blog
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while creating the blog.")

@blog_router.put("/{blog_id}", response_model=BlogResponse)
def update_existing_blog(blog_id: int, updated_blog: BlogCreate, db: Session = Depends(get_db)):
    """
    Update an existing blog by ID.
    """
    try:
        blog = db.query(Blog).filter(Blog.id == blog_id).first()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while fetching the blog.")
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found.")

    try:
        blog.title = updated_blog.title
        blog.content = updated_blog.content
        blog.author = updated_blog.author
        db.commit()
        db.refresh(blog)
        return blog
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while updating the blog.")

@blog_router.delete("/{blog_id}")
def delete_existing_blog(blog_id: int, db: Session = Depends(get_db)):
    """
    Delete a blog entry by ID.
    """
    try:
        blog = db.query(Blog).filter(Blog.id == blog_id).first()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred while fetching the blog.")
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found.")

    try:
        db.delete(blog)
        db.commit()
        return {"message": "Blog deleted successfully."}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while deleting the blog.")
