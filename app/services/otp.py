# Placeholder OTP service functions
from sqlalchemy.orm import Session
from app.models.otp import OTP
from app.models.user import User


def create_otp_secret(db: Session, user: User, secret: str) -> OTP:
    # Future implementation: create or rotate secret
    otp = OTP(user_id=user.id, secret=secret)
    db.add(otp)
    db.commit()
    db.refresh(otp)
    return otp
