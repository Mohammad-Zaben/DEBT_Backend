from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class EmployerBase(BaseModel):
    name: str
    contact_info: Optional[str] = None


class EmployerCreate(EmployerBase):
    pass


class EmployerRead(EmployerBase):
    id: int
    created_by: int
    created_at: datetime
    payment_count: int = 0  # Number of work payments from this employer

    class Config:
        from_attributes = True


class EmployerUpdate(BaseModel):
    name: Optional[str] = None
    contact_info: Optional[str] = None


# Work Payment Schemas
class WorkPaymentBase(BaseModel):
    employer_id: int
    amount: Decimal
    description: Optional[str] = None
    payment_date: Optional[datetime] = None  # If not provided, uses current time


class WorkPaymentCreate(WorkPaymentBase):
    pass


class WorkPaymentRead(WorkPaymentBase):
    id: int
    provider_id: int
    employer_name: str  # Include employer name for easy display
    created_at: datetime

    class Config:
        from_attributes = True


class WorkPaymentSummary(BaseModel):
    """Summary of work payments for a provider"""
    total_payments: int
    total_amount: Decimal
    employers_count: int
    last_payment_date: Optional[datetime] = None