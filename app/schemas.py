from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class ContactForm(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    contact_no: Optional[str] = None
    message: str = Field(..., min_length=5)
