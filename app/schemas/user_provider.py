from datetime import datetime
from pydantic import BaseModel

class UserProviderLinkBase(BaseModel):
    user_id: int
    provider_id: int

class UserProviderLinkCreate(UserProviderLinkBase):
    pass

class UserProviderLinkRead(UserProviderLinkBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
