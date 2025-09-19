from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from typing import Optional
from app.models.transaction import TransactionType, TransactionStatus

class TransactionBase(BaseModel):
    user_id: int
    provider_id: int
    type: TransactionType
    amount: Decimal
    pass

class TransactionCreate(BaseModel):
    user_id: int
    type: TransactionType
    amount: Decimal
    otp: Optional[str] = None  # Required for DEBT transactions

class DebtApprove(BaseModel):
    transaction_id: int
    # future: otp_code: str

class TransactionRead(TransactionBase):
    id: int
    status: TransactionStatus
    date: datetime

    class Config:
        from_attributes = True

class BalanceSummary(BaseModel):
    user_id: int
    provider_id: int
    total_debt: Decimal
    total_payments: Decimal
    balance: Decimal
