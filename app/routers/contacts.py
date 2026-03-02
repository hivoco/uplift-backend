import math
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_admin
from app.models import Contact
from app.schemas import ContactResponse, PaginatedResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
def list_contacts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin),
):
    total = db.query(Contact).count()
    total_pages = math.ceil(total / per_page) if total > 0 else 1

    contacts = (
        db.query(Contact)
        .order_by(Contact.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return PaginatedResponse(
        items=[ContactResponse.model_validate(c) for c in contacts],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )
