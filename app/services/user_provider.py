from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.user_provider import UserProvider


def link_user_provider(db: Session, provider: User, client: User):
    # Authorization: provider must be Provider role
    if provider.role != UserRole.PROVIDER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only providers can link clients")
    # Prevent duplicate
    existing = db.query(UserProvider).filter(UserProvider.user_id == client.id, UserProvider.provider_id == provider.id).first()
    if existing:
        return existing
    link = UserProvider(user_id=client.id, provider_id=provider.id)
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


def get_provider_clients(db: Session, provider: User):
    if provider.role != UserRole.PROVIDER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a provider")
    return [l.user for l in provider.client_links]


def get_client_providers(db: Session, client: User):
    return [l.provider for l in client.provider_links]
