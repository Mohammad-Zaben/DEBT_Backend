from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from app.models.user import UserRole, ProviderType

class UserLoginResponse(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole
    provider_type: Optional[ProviderType] = None
    secret_key: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserLoginResponse

class TokenPayload(BaseModel):
    sub: str
    role: str
    exp: int
