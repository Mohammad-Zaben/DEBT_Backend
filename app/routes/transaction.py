from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal
from app.core.database import get_db
from app.utils.dependencies import get_current_user
from app.models.user import User, UserRole
from app.schemas.transaction import TransactionCreate, TransactionRead, DebtApprove, BalanceSummary
from app.models.transaction import TransactionType
from app.services.transaction import create_transaction, approve_debt, list_transactions_for_pair, compute_balance

router = APIRouter()

@router.post("/", response_model=TransactionRead)
def create(payload: TransactionCreate, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current.role != UserRole.PROVIDER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only providers can create transactions")
    tx = create_transaction(db, current, payload.user_id, payload.amount, payload.type)
    return TransactionRead.model_validate(tx)

@router.post("/approve", response_model=TransactionRead)
def approve(payload: DebtApprove, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tx = approve_debt(db, current, payload.transaction_id)
    return TransactionRead.model_validate(tx)

@router.get("/pair/{user_id}/{provider_id}", response_model=list[TransactionRead])
def list_pair(user_id: int, provider_id: int, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    txs = list_transactions_for_pair(db, current, user_id, provider_id)
    return [TransactionRead.model_validate(tx) for tx in txs]

@router.get("/balance/{user_id}/{provider_id}", response_model=BalanceSummary)
def balance(user_id: int, provider_id: int, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    summary = compute_balance(db, current, user_id, provider_id)
    return BalanceSummary.model_validate(summary)
