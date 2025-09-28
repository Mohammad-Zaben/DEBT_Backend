from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import user
from app.schemas.user import UserCreate, UserRead, UserLogin, ProviderCreate
from app.schemas.auth import Token
from app.services import user as user_service
from app.services import auth as auth_service
from app.models.user import UserRole, User
from app.utils.dependencies import get_current_user

router = APIRouter()

@router.post("/register", response_model=UserRead, include_in_schema=True)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    - Creates a regular USER account only
    - To become a provider, use the separate /provider endpoint (admin only)
    """
    new_user = user_service.create_user(
        db,
        name=payload.name,
        email=payload.email,
        password=payload.password,
        role=UserRole.USER,
        provider_type=None  # Users are always created without provider type
    )
    return UserRead.model_validate(new_user)

@router.post("/provider", response_model=UserRead)
def create_provider(payload: ProviderCreate, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Create a new provider (Admin only)
    - Admin can create providers with specific provider type
    - provider_type is required for provider creation
    """
    if current.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can create providers",
        )
    provider = user_service.create_user(
        db,
        name=payload.name,
        email=payload.email,
        password=payload.password,
        role=UserRole.PROVIDER,
        provider_type=payload.provider_type
    )
    return UserRead.model_validate(provider)

@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    login_response = auth_service.login(db, payload.email, payload.password)
    return login_response
