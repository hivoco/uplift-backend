import os
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

ADMIN_EMAILS = [
    e.strip() for e in os.getenv("ADMIN_EMAILS", "").split(",") if e.strip()
]
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24
OTP_EXPIRY_MINUTES = 5
CMS_ORIGIN = os.getenv("CMS_ORIGIN", "http://localhost:5173")
