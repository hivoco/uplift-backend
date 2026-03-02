from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_admin
from app.models import FAQ
from app.schemas import FAQCreate, FAQUpdate, FAQResponse

router = APIRouter()
public_router = APIRouter()


# --- Protected CMS endpoints ---

@router.get("", response_model=list[FAQResponse])
def list_faqs(
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin),
):
    return db.query(FAQ).order_by(FAQ.sort_order.asc()).all()


@router.get("/{faq_id}", response_model=FAQResponse)
def get_faq(
    faq_id: int,
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin),
):
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return faq


@router.post("", response_model=FAQResponse)
def create_faq(
    data: FAQCreate,
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin),
):
    faq = FAQ(
        question=data.question,
        answer=data.answer,
        sort_order=data.sort_order,
    )
    db.add(faq)
    db.commit()
    db.refresh(faq)
    return faq


@router.put("/{faq_id}", response_model=FAQResponse)
def update_faq(
    faq_id: int,
    data: FAQUpdate,
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin),
):
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")

    if data.question is not None:
        faq.question = data.question
    if data.answer is not None:
        faq.answer = data.answer
    if data.sort_order is not None:
        faq.sort_order = data.sort_order
    if data.is_active is not None:
        faq.is_active = data.is_active

    db.commit()
    db.refresh(faq)
    return faq


@router.delete("/{faq_id}")
def delete_faq(
    faq_id: int,
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin),
):
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")

    db.delete(faq)
    db.commit()
    return {"message": "FAQ deleted successfully"}


# --- Public endpoint ---

@public_router.get("", response_model=list[FAQResponse])
def list_public_faqs(db: Session = Depends(get_db)):
    return (
        db.query(FAQ)
        .filter(FAQ.is_active == True)
        .order_by(FAQ.sort_order.asc())
        .all()
    )
