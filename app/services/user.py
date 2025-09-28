from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, UserRole, ProviderType
from app.core.security import get_password_hash
from typing import Optional


def create_user(
    db: Session, 
    name: str, 
    email: str, 
    password: str, 
    role: UserRole = UserRole.USER,
    provider_type: Optional[ProviderType] = None
) -> User:
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    # Validate provider_type is only set for providers
    if provider_type is not None and role != UserRole.PROVIDER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Provider type can only be set for provider role"
        )
    
    user = User(
        name=name, 
        email=email, 
        password=get_password_hash(password), 
        role=role,
        provider_type=provider_type,
        secret_key=User.generate_secret_key()  # Generate unique secret key
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_public_info(db: Session, user_id: int) -> User:
    """
    Get public user information (id, name, email) by user ID
    Raises HTTPException if user not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
