from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole, ProviderType

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    # No provider_type here - users register as regular users only

class ProviderCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    provider_type: ProviderType  # Required for provider registration

class UserRead(UserBase):
    id: int
    role: UserRole
    provider_type: Optional[ProviderType] = None
    secret_key: Optional[str] = None  # Include secret key in user response
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None
    provider_type: Optional[ProviderType] = None  # Allow updating provider type

class ProviderTypeUpdate(BaseModel):
    provider_type: ProviderType

class UserPublicInfo(BaseModel):
    """Schema for public user information (name and email only)"""
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True
