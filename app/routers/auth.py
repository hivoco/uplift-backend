from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import bcrypt

from app.deps import get_db
from app.config import ADMIN_EMAILS, ADMIN_PASSWORD_HASH, OTP_EXPIRY_MINUTES
from app.models import OTP
from app.schemas import LoginRequest, OTPVerifyRequest
from app.utils import generate_otp, create_access_token
from app.email_service import send_otp_email

router = APIRouter()


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    if data.email not in ADMIN_EMAILS:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not bcrypt.checkpw(data.password.encode(), ADMIN_PASSWORD_HASH.encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    otp_code = generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES)

    otp = OTP(
        email=data.email,
        otp_code=otp_code,
        expires_at=expires_at,
    )
    db.add(otp)
    db.commit()

    try:
        send_otp_email(data.email, otp_code)
    except Exception:
        pass

    return {"message": "OTP sent to your email"}


@router.post("/verify-otp")
def verify_otp(data: OTPVerifyRequest, db: Session = Depends(get_db)):
    otp = (
        db.query(OTP)
        .filter(
            OTP.email == data.email,
            OTP.is_used == False,
        )
        .order_by(OTP.created_at.desc())
        .first()
    )

    if not otp:
        raise HTTPException(status_code=400, detail="No OTP found. Please login again.")

    now = datetime.now(timezone.utc)
    if otp.expires_at.replace(tzinfo=timezone.utc) < now:
        raise HTTPException(status_code=400, detail="OTP has expired. Please login again.")

    if otp.otp_code != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    otp.is_used = True
    db.commit()

    access_token = create_access_token(data.email)
    return {"access_token": access_token, "token_type": "bearer"}
