import re
import random
import string
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRY_HOURS


def generate_otp(length=6) -> str:
    return ''.join(random.choices(string.digits, k=length))


def create_access_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS)
    payload = {"sub": email, "exp": expire}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')
