from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.utils.dependencies import get_current_user
from app.schemas.user import UserRead
from app.models.user import User
from app.services.user_provider import get_client_providers

router = APIRouter()

@router.get("/me", response_model=UserRead)
def read_me(current: User = Depends(get_current_user)):
    return UserRead.model_validate(current)

@router.get("/me/providers", response_model=list[UserRead])
def my_providers(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    providers = get_client_providers(db, current)
    return [UserRead.model_validate(provider) for provider in providers]
