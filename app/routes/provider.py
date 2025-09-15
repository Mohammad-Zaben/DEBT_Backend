from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.utils.dependencies import get_current_user
from app.schemas.user import UserRead
from app.models.user import User, UserRole
from app.services.user_provider import get_provider_clients

router = APIRouter()

@router.get("/me/clients", response_model=list[UserRead])
def my_clients(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current.role != UserRole.PROVIDER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a provider")
    clients = get_provider_clients(db, current)
    return [UserRead.model_validate(client) for client in clients]
