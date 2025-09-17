from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models.user import User, UserRole
from app.models.user_provider import UserProvider, LinkStatus


def link_user_provider(db: Session, provider: User, client: User):
    # Authorization: provider must be Provider role
    if provider.role != UserRole.PROVIDER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only providers can link clients")
    # Prevent duplicate
    existing = db.query(UserProvider).filter(UserProvider.user_id == client.id, UserProvider.provider_id == provider.id).first()
    if existing:
        return existing
    link = UserProvider(user_id=client.id, provider_id=provider.id, status=LinkStatus.PENDING)
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


def get_provider_clients(db: Session, provider: User):
    if provider.role != UserRole.PROVIDER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a provider")
    return [l.user for l in provider.client_links if l.status == LinkStatus.APPROVED]


def get_client_providers(db: Session, client: User):
    return [l.provider for l in client.provider_links if l.status == LinkStatus.APPROVED]


def get_user_invitations(db: Session, user: User) -> List[UserProvider]:
    """Get all pending invitations for a user"""
    return db.query(UserProvider).filter(
        UserProvider.user_id == user.id,
        UserProvider.status == LinkStatus.PENDING
    ).all()


def get_provider_applications(db: Session, provider: User) -> List[UserProvider]:
    """Get all applications (pending and decided) for a provider"""
    if provider.role != UserRole.PROVIDER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a provider")
    return db.query(UserProvider).filter(UserProvider.provider_id == provider.id).all()


def update_link_status(db: Session, link_id: int, user: User, new_status: LinkStatus) -> UserProvider:
    """Update the status of a user-provider link"""
    link = db.query(UserProvider).filter(UserProvider.id == link_id).first()
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")
    
    # Only the user (client) can approve/reject invitations
    if link.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only manage your own invitations")
    
    # Can only update pending invitations
    if link.status != LinkStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can only update pending invitations")
    
    link.status = new_status
    db.commit()
    db.refresh(link)
    return link
