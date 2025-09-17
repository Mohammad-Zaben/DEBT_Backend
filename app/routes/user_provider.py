from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.utils.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.user_provider import UserProvider, LinkStatus
from app.schemas.user_provider import (
    UserProviderLinkCreate, 
    UserProviderLinkRead,
    UserProviderInvitationRead,
    UserProviderApplicationRead,
    UserProviderStatusUpdate,
    LinkedProviderRead,
    LinkedClientRead
)
from app.services.user_provider import (
    link_user_provider,
    get_user_invitations,
    get_provider_applications,
    update_link_status,
    get_client_providers
)
from app.services.user import get_user

router = APIRouter()

@router.post("/link", response_model=UserProviderLinkRead)
def link(payload: UserProviderLinkCreate, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Create a link between provider and client
    WHO CAN USE: PROVIDER only
    - Provider can link themselves to a client by specifying client's user_id
    """
    # Only provider can link specifying client id
    if current.role != UserRole.PROVIDER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only providers can link clients")
    client = get_user(db, payload.user_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    link_obj = link_user_provider(db, current, client)
    return UserProviderLinkRead.model_validate(link_obj)


@router.get("/invitations", response_model=List[UserProviderInvitationRead])
def get_my_invitations(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get all pending invitations for the current user
    WHO CAN USE: CLIENT/USER only
    - Users can see all provider invitations they have received
    """
    invitations = get_user_invitations(db, current)
    return [
        UserProviderInvitationRead(
            id=inv.id,
            provider_id=inv.provider_id,
            provider_name=inv.provider.name,
            provider_email=inv.provider.email,
            status=inv.status,
            created_at=inv.created_at
        )
        for inv in invitations
    ]


@router.put("/invitations/{invitation_id}/status", response_model=UserProviderLinkRead)
def update_invitation_status(
    invitation_id: int,
    payload: UserProviderStatusUpdate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve or reject an invitation
    WHO CAN USE: CLIENT/USER only
    - Users can approve or reject provider invitations they have received
    """
    updated_link = update_link_status(db, invitation_id, current, payload.status)
    return UserProviderLinkRead.model_validate(updated_link)


@router.get("/applications", response_model=List[UserProviderApplicationRead])
def get_my_applications(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get all applications for the current provider
    WHO CAN USE: PROVIDER only
    - Providers can see all client applications/link requests they have received
    """
    applications = get_provider_applications(db, current)
    return [
        UserProviderApplicationRead(
            id=app.id,
            user_id=app.user_id,
            user_name=app.user.name,
            user_email=app.user.email,
            status=app.status,
            created_at=app.created_at
        )
        for app in applications
    ]


@router.get("/my-providers", response_model=List[LinkedProviderRead])
def get_my_providers(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get all linked providers for the current user
    WHO CAN USE: CLIENT/USER only
    - Users can see all providers they are linked with (approved links only)
    """
    # Get all approved provider links for the current user
    provider_links = db.query(UserProvider).filter(
        UserProvider.user_id == current.id,
        UserProvider.status == LinkStatus.APPROVED
    ).all()
    
    return [
        LinkedProviderRead(
            id=link.id,
            provider_id=link.provider_id,
            provider_name=link.provider.name,
            provider_email=link.provider.email,
            status=link.status,
            created_at=link.created_at
        )
        for link in provider_links
    ]


@router.get("/my-clients", response_model=List[LinkedClientRead])
def get_my_clients(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get all linked clients for the current provider
    WHO CAN USE: PROVIDER only
    - Providers can see all clients they are linked with (approved links only)
    """
    # Check if current user is a provider
    if current.role != UserRole.PROVIDER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only providers can access client list")
    
    # Get all approved client links for the current provider
    client_links = db.query(UserProvider).filter(
        UserProvider.provider_id == current.id,
        UserProvider.status == LinkStatus.APPROVED
    ).all()
    
    return [
        LinkedClientRead(
            id=link.id,
            user_id=link.user_id,
            user_name=link.user.name,
            user_email=link.user.email,
            status=link.status,
            created_at=link.created_at
        )
        for link in client_links
    ]
