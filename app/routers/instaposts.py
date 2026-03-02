from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_admin
from app.models import InstaPost
from app.schemas import InstaPostCreate, InstaPostUpdate, InstaPostResponse

router = APIRouter()
public_router = APIRouter()


# --- Protected CMS endpoints ---

@router.get("", response_model=list[InstaPostResponse])
def list_insta_posts(
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin),
):
    return db.query(InstaPost).order_by(InstaPost.sort_order.asc(), InstaPost.created_at.desc()).all()


@router.post("", response_model=InstaPostResponse)
def create_insta_post(
    data: InstaPostCreate,
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin),
):
    post = InstaPost(post_url=data.post_url, sort_order=data.sort_order)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.put("/{post_id}", response_model=InstaPostResponse)
def update_insta_post(
    post_id: int,
    data: InstaPostUpdate,
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin),
):
    post = db.query(InstaPost).filter(InstaPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if data.sort_order is not None:
        post.sort_order = data.sort_order
    db.commit()
    db.refresh(post)
    return post


@router.delete("/{post_id}")
def delete_insta_post(
    post_id: int,
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin),
):
    post = db.query(InstaPost).filter(InstaPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(post)
    db.commit()
    return {"message": "Post deleted successfully"}


# --- Public endpoint ---

@public_router.get("", response_model=list[InstaPostResponse])
def list_public_insta_posts(db: Session = Depends(get_db)):
    return db.query(InstaPost).order_by(InstaPost.sort_order.asc(), InstaPost.created_at.desc()).all()
