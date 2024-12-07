from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.db import get_db
from src.models.blog import Blog
from src.schemas.blog import BlogCreate, BlogResponse

blog_router = APIRouter()


@blog_router.get("/", response_model=list[BlogResponse])
def read_blogs(db: Session = Depends(get_db)):
    return db.query(Blog).all()


@blog_router.get("/{blog_id}", response_model=BlogResponse)
def read_blog(blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return blog


@blog_router.post("/", response_model=BlogResponse)
def create_new_blog(blog: BlogCreate, db: Session = Depends(get_db)):
    new_blog = Blog(**blog.dict())
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


@blog_router.put("/{blog_id}", response_model=BlogResponse)
def update_existing_blog(blog_id: int, updated_blog: BlogCreate, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    blog.title = updated_blog.title
    blog.content = updated_blog.content
    blog.author = updated_blog.author
    db.commit()
    db.refresh(blog)
    return blog


@blog_router.delete("/{blog_id}")
def delete_existing_blog(blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    db.delete(blog)
    db.commit()
    return {"message": "Blog deleted successfully"}
