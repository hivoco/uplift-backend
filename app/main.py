from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.schemas import ContactForm
from app.email_service import send_contact_email
from app.database import Base, engine
from app.models import Contact
from app.deps import get_db

app = FastAPI(
    title="Uplife Contact API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://liveuplife.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/contact")
def contact_form(
    data: ContactForm,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    try:
        # 1. Save to database (SYNC – must succeed)
        contact = Contact(
            name=data.name,
            email=data.email,
            contact_no=data.contact_no,
            message=data.message,
        )
        db.add(contact)
        db.commit()

        # 2. Send email (ASYNC / BACKGROUND)
        background_tasks.add_task(
            send_contact_email,
            data.name,
            data.email,
            data.contact_no,
            data.message,
        )

        return {
            "success": True,
            "message": "Contact form submitted successfully",
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to process contact form",
        )
