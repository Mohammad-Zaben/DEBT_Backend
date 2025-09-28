from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import verify_password, create_access_token
from app.schemas.auth import UserLoginResponse


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return user


def login(db: Session, email: str, password: str):
    user = authenticate_user(db, email, password)
    token = create_access_token(subject=str(user.id), role=user.role.value)
    user_response = UserLoginResponse.model_validate(user)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_response
    }
