from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.utils.dependencies import get_current_user
from app.schemas.user import UserRead, ProviderTypeUpdate, UserPublicInfo
from app.models.user import User, UserRole
from app.services.user_provider import get_client_providers
from app.services.user import get_user_public_info

router = APIRouter()

@router.get("/me", response_model=UserRead)
def read_me(current: User = Depends(get_current_user)):
    """
    Get current user information
    WHO CAN USE: Any authenticated user
    """
    return UserRead.model_validate(current)

@router.get("/me/providers", response_model=list[UserRead])
def my_providers(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get all linked providers for current user
    WHO CAN USE: CLIENT/USER only
    """
    providers = get_client_providers(db, current)
    return [UserRead.model_validate(provider) for provider in providers]

@router.put("/me/provider-type", response_model=UserRead)
def update_provider_type(
    payload: ProviderTypeUpdate, 
    current: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Update provider type for current user
    WHO CAN USE: PROVIDER only
    - LENDER: Can add debts and payments (shopkeeper/market owner)
    - PAYER: Can only add payments (contractor)
    """
    if current.role != UserRole.PROVIDER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only providers can set provider type"
        )
    
    current.provider_type = payload.provider_type
    db.commit()
    db.refresh(current)
    
    return UserRead.model_validate(current)


@router.get("/{user_id}/public", response_model=UserPublicInfo)
def get_user_public_info_endpoint(user_id: int, db: Session = Depends(get_db)):
    """
    Get public user information (id, name, email) by user ID
    WHO CAN USE: Anyone (no authentication required)
    
    This endpoint allows you to get basic public information about a user
    before sending them an application or request.
    """
    user = get_user_public_info(db, user_id)
    return UserPublicInfo.model_validate(user)
