import os
import math
import uuid
import logging
from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from typing import Optional

logger = logging.getLogger(__name__)

from app.deps import get_db, get_current_admin
from app.models import Blog
from app.schemas import BlogResponse, BlogListResponse, PaginatedResponse
from app.utils import slugify

router = APIRouter()
public_router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "blog_images")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def save_image(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid image format")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(file.file.read())
    return f"/uploads/blog_images/{filename}"


def delete_image(image_url: str):
    if image_url:
        filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), image_url.lstrip("/"))
        if os.path.exists(filepath):
            os.remove(filepath)


def generate_unique_slug(db: Session, title: str, exclude_id: int = None) -> str:
    base_slug = slugify(title)
    slug = base_slug
    counter = 2
    while True:
        query = db.query(Blog).filter(Blog.slug == slug)
        if exclude_id:
            query = query.filter(Blog.id != exclude_id)
        if not query.first():
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1


# --- Protected CMS endpoints ---

@router.get("", response_model=PaginatedResponse)
def list_blogs(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin),
):
    total = db.query(Blog).count()
    total_pages = math.ceil(total / per_page) if total > 0 else 1

    blogs = (
        db.query(Blog)
        .order_by(Blog.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return PaginatedResponse(
        items=[BlogListResponse.model_validate(b) for b in blogs],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.get("/{blog_id}", response_model=BlogResponse)
def get_blog(
    blog_id: int,
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin),
):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return BlogResponse.model_validate(blog)


@router.post("/upload-image")
def upload_blog_image(
    image: UploadFile = File(...),
    admin: str = Depends(get_current_admin),
):
    url = save_image(image)
    return {"url": url}


@router.post("", response_model=BlogResponse)
def create_blog(
    title: str = Form(...),
    content: str = Form(...),
    excerpt: Optional[str] = Form(None),
    is_published: str = Form("false"),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin),
):
    published = is_published.lower() in ("true", "1", "yes")
    slug = generate_unique_slug(db, title)
    image_url = save_image(image) if image and image.filename else None

    blog = Blog(
        title=title,
        slug=slug,
        content=content,
        excerpt=excerpt,
        image_url=image_url,
        is_published=published,
    )
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return BlogResponse.model_validate(blog)


@router.put("/{blog_id}", response_model=BlogResponse)
def update_blog(
    blog_id: int,
    title: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    excerpt: Optional[str] = Form(None),
    is_published: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin),
):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    if title is not None:
        blog.title = title
        blog.slug = generate_unique_slug(db, title, exclude_id=blog_id)
    if content is not None:
        blog.content = content
    if excerpt is not None:
        blog.excerpt = excerpt
    if is_published is not None:
        blog.is_published = is_published.lower() in ("true", "1", "yes")
    if image and image.filename:
        delete_image(blog.image_url)
        blog.image_url = save_image(image)

    db.commit()
    db.refresh(blog)
    return BlogResponse.model_validate(blog)


@router.delete("/{blog_id}")
def delete_blog(
    blog_id: int,
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin),
):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    delete_image(blog.image_url)
    db.delete(blog)
    db.commit()
    return {"message": "Blog deleted successfully"}


# --- Public endpoints ---

@public_router.get("", response_model=PaginatedResponse)
def list_public_blogs(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Blog).filter(Blog.is_published == True)
    total = query.count()
    total_pages = math.ceil(total / per_page) if total > 0 else 1

    blogs = (
        query.order_by(Blog.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return PaginatedResponse(
        items=[BlogListResponse.model_validate(b) for b in blogs],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@public_router.get("/{slug}", response_model=BlogResponse)
def get_public_blog(slug: str, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.slug == slug, Blog.is_published == True).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return BlogResponse.model_validate(blog)
