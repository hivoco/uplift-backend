from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Blog, FAQ, InstaPost
from app.schemas import BlogListResponse, FAQResponse, InstaPostResponse, HomePageResponse

router = APIRouter()


@router.get("/home", response_model=HomePageResponse)
def get_home_data(
    blog_limit: int = Query(6, ge=1, le=20),
    db: Session = Depends(get_db),
):
    """Combined homepage data: latest blogs, active FAQs, and insta posts."""
    blogs = (
        db.query(Blog)
        .filter(Blog.is_published == True)
        .order_by(Blog.created_at.desc())
        .limit(blog_limit)
        .all()
    )

    faqs = (
        db.query(FAQ)
        .filter(FAQ.is_active == True)
        .order_by(FAQ.sort_order.asc())
        .all()
    )

    insta_posts = (
        db.query(InstaPost)
        .order_by(InstaPost.sort_order.asc(), InstaPost.created_at.desc())
        .all()
    )

    return HomePageResponse(
        blogs=[BlogListResponse.model_validate(b) for b in blogs],
        faqs=[FAQResponse.model_validate(f) for f in faqs],
        insta_posts=[InstaPostResponse.model_validate(p) for p in insta_posts],
    )
