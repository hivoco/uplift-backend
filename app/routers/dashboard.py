from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import datetime, timedelta, timezone

from app.deps import get_db, get_current_admin
from app.models import Contact, Blog, FAQ
from app.schemas import DashboardStats, DailyCount, ContactResponse, BlogListResponse, FAQResponse

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin),
):
    total_contacts = db.query(func.count(Contact.id)).scalar()
    total_blogs = db.query(func.count(Blog.id)).scalar()
    total_faqs = db.query(func.count(FAQ.id)).scalar()

    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    weekly_contacts = (
        db.query(func.count(Contact.id))
        .filter(Contact.created_at >= seven_days_ago)
        .scalar()
    )

    daily_rows = (
        db.query(
            cast(Contact.created_at, Date).label("date"),
            func.count(Contact.id).label("count"),
        )
        .filter(Contact.created_at >= seven_days_ago)
        .group_by(cast(Contact.created_at, Date))
        .order_by(cast(Contact.created_at, Date))
        .all()
    )

    daily_contacts = [
        DailyCount(date=str(row.date), count=row.count)
        for row in daily_rows
    ]

    recent_contacts = (
        db.query(Contact)
        .order_by(Contact.created_at.desc())
        .limit(5)
        .all()
    )

    recent_blogs = (
        db.query(Blog)
        .order_by(Blog.created_at.desc())
        .limit(5)
        .all()
    )

    recent_faqs = (
        db.query(FAQ)
        .order_by(FAQ.created_at.desc())
        .limit(5)
        .all()
    )

    return DashboardStats(
        total_contacts=total_contacts,
        total_blogs=total_blogs,
        total_faqs=total_faqs,
        weekly_contacts=weekly_contacts,
        daily_contacts=daily_contacts,
        recent_contacts=[ContactResponse.model_validate(c) for c in recent_contacts],
        recent_blogs=[BlogListResponse.model_validate(b) for b in recent_blogs],
        recent_faqs=[FAQResponse.model_validate(f) for f in recent_faqs],
    )
