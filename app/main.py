import os
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session

from app.schemas import ContactForm
from app.email_service import send_contact_email
from app.database import Base, engine
from app.models import Contact
from app.deps import get_db
from app.config import CMS_ORIGIN
from app.routers import auth, contacts, blogs, faqs, dashboard, instaposts, public

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Uplife API",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error on {request.method} {request.url.path}: {exc.errors()}")
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

# Static files for blog image uploads
uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(os.path.join(uploads_dir, "blog_images"), exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://liveuplife.com", CMS_ORIGIN,"http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CMS routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(contacts.router, prefix="/contacts", tags=["Contacts"])
app.include_router(blogs.router, prefix="/blogs", tags=["Blogs"])
app.include_router(faqs.router, prefix="/faqs", tags=["FAQs"])
app.include_router(instaposts.router, prefix="/insta-posts", tags=["InstaPost"])

# Public routers
app.include_router(blogs.public_router, prefix="/public/blogs", tags=["Public Blogs"])
app.include_router(faqs.public_router, prefix="/public/faqs", tags=["Public FAQs"])
app.include_router(instaposts.public_router, prefix="/public/insta-posts", tags=["Public InstaPost"])
app.include_router(public.router, prefix="/public", tags=["Public Home"])


# Public contact form endpoint
@app.post("/contact")
def contact_form(
    data: ContactForm,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    try:
        contact = Contact(
            name=data.name,
            email=data.email,
            contact_no=data.contact_no,
            message=data.message,
        )
        db.add(contact)
        db.commit()

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
        logger.error(f"Contact form error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process contact form: {str(e)}",
        )
