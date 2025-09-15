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
    new_user = user_service.create_user(
        db,
        name=payload.name,
        email=payload.email,
        password=payload.password,
        role=UserRole.USER,
    )
    return UserRead.model_validate(new_user)

@router.post("/provider", response_model=UserRead)
def create_provider(payload: ProviderCreate, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
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
    )
    return UserRead.model_validate(provider)

@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    token = auth_service.login(db, payload.email, payload.password)
    return {"access_token": token, "token_type": "bearer"}
