from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import datetime


# --- Contact ---
class ContactForm(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    contact_no: Optional[str] = None
    message: str = Field(..., min_length=5)


class ContactResponse(BaseModel):
    id: int
    name: str
    email: str
    contact_no: Optional[str]
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Auth ---
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)


# --- Blog ---
class BlogCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    excerpt: Optional[str] = Field(None, max_length=500)
    is_published: bool = False


class BlogUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    excerpt: Optional[str] = Field(None, max_length=500)
    is_published: Optional[bool] = None


class BlogResponse(BaseModel):
    id: int
    title: str
    slug: str
    content: str
    excerpt: Optional[str]
    image_url: Optional[str]
    is_published: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BlogListResponse(BaseModel):
    id: int
    title: str
    slug: str
    excerpt: Optional[str]
    image_url: Optional[str]
    is_published: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- FAQ ---
class FAQCreate(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)
    answer: str = Field(..., min_length=1)
    sort_order: int = 0


class FAQUpdate(BaseModel):
    question: Optional[str] = Field(None, max_length=500)
    answer: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class FAQResponse(BaseModel):
    id: int
    question: str
    answer: str
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- InstaPost ---
class InstaPostCreate(BaseModel):
    post_url: str = Field(..., min_length=1)
    sort_order: int = 0


class InstaPostUpdate(BaseModel):
    sort_order: Optional[int] = None


class InstaPostResponse(BaseModel):
    id: int
    post_url: str
    sort_order: int
    created_at: datetime

    class Config:
        from_attributes = True


# --- Pagination ---
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    per_page: int
    total_pages: int


# --- Public Home ---
class HomePageResponse(BaseModel):
    blogs: List[Any]
    faqs: List[Any]
    insta_posts: List[Any]


# --- Dashboard ---
class DailyCount(BaseModel):
    date: str
    count: int


class DashboardStats(BaseModel):
    total_contacts: int
    total_blogs: int
    total_faqs: int
    weekly_contacts: int
    daily_contacts: List[DailyCount]
    recent_contacts: List[ContactResponse]
    recent_blogs: List[BlogListResponse]
    recent_faqs: List[FAQResponse]
