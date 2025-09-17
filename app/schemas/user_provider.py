from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.user_provider import LinkStatus

class UserProviderLinkBase(BaseModel):
    user_id: int
    provider_id: int

class UserProviderLinkCreate(BaseModel):
    user_id: int

class UserProviderLinkRead(UserProviderLinkBase):
    id: int
    status: LinkStatus
    created_at: datetime

    class Config:
        from_attributes = True

class UserProviderInvitationRead(BaseModel):
    id: int
    provider_id: int
    provider_name: str
    provider_email: str
    status: LinkStatus
    created_at: datetime

    class Config:
        from_attributes = True

class UserProviderApplicationRead(BaseModel):
    id: int
    user_id: int
    user_name: str
    user_email: str
    status: LinkStatus
    created_at: datetime

    class Config:
        from_attributes = True

class UserProviderStatusUpdate(BaseModel):
    status: LinkStatus

class LinkedProviderRead(BaseModel):
    id: int
    provider_id: int
    provider_name: str
    provider_email: str
    status: LinkStatus
    created_at: datetime

    class Config:
        from_attributes = True

class LinkedClientRead(BaseModel):
    id: int
    user_id: int
    user_name: str
    user_email: str
    status: LinkStatus
    created_at: datetime

    class Config:
        from_attributes = True
