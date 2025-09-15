from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.utils.dependencies import get_current_user
from app.models.user import User, UserRole
from app.schemas.user_provider import UserProviderLinkCreate, UserProviderLinkRead
from app.services.user_provider import link_user_provider
from app.services.user import get_user

router = APIRouter()

@router.post("/link", response_model=UserProviderLinkRead)
def link(payload: UserProviderLinkCreate, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Only provider can link specifying client id
    if current.role != UserRole.PROVIDER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only providers can link clients")
    client = get_user(db, payload.user_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    link_obj = link_user_provider(db, current, client)
    return UserProviderLinkRead.model_validate(link_obj)
