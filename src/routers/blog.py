from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.db import get_db
from src.models.blog import Blog
from src.schemas.blog import BlogCreate, BlogResponse

blog_router = APIRouter()


@blog_router.get("/", response_model=list[BlogResponse])
def read_blogs(db: Session = Depends(get_db)):
    """
    Retrieve all blogs from the database.
    """
    try:
        blogs = db.query(Blog).all()
        if not blogs:
            raise HTTPException(status_code=404, detail="No blogs found.")
        return blogs
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


@blog_router.get("/{blog_id}", response_model=BlogResponse)
def read_blog(blog_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific blog by ID.
    """
    try:
        blog = db.query(Blog).filter(Blog.id == blog_id).first()
        if not blog:
            raise HTTPException(status_code=404, detail="Blog not found.")
        return blog
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


@blog_router.post("/create_blogs", response_model=BlogResponse)
def create_new_blog(blog: BlogCreate, db: Session = Depends(get_db)):
    """
    Create a new blog entry.
    """
    try:
        new_blog = Blog(**blog.dict())
        db.add(new_blog)
        db.commit()
        db.refresh(new_blog)
        return new_blog
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while creating the blog.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


@blog_router.put("/{blog_id}", response_model=BlogResponse)
def update_existing_blog(blog_id: int, updated_blog: BlogCreate, db: Session = Depends(get_db)):
    """
    Update an existing blog by ID.
    """
    try:
        blog = db.query(Blog).filter(Blog.id == blog_id).first()
        if not blog:
            raise HTTPException(status_code=404, detail="Blog not found.")

        blog.title = updated_blog.title
        blog.content = updated_blog.content
        blog.author = updated_blog.author

        db.commit()
        db.refresh(blog)
        return blog
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while updating the blog.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


@blog_router.delete("/{blog_id}")
def delete_existing_blog(blog_id: int, db: Session = Depends(get_db)):
    """
    Delete a blog entry by ID.
    """
    try:
        blog = db.query(Blog).filter(Blog.id == blog_id).first()
        if not blog:
            raise HTTPException(status_code=404, detail="Blog not found.")

        db.delete(blog)
        db.commit()
        return {"message": "Blog deleted successfully."}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while deleting the blog.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
