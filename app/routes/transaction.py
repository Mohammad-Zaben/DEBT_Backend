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
    """
    Create a transaction
    WHO CAN USE: PROVIDER only
    
    Provider Type Restrictions:
    - LENDER providers: Can create both DEBT and PAYMENT transactions
    - PAYER providers: Can only create PAYMENT transactions (contractor paying workers)
    
    Transaction Types:
    - DEBT: Records money owed by user to provider (requires user approval)
    - PAYMENT: Records money paid to user by provider (automatically confirmed)
    """
    if current.role != UserRole.PROVIDER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only providers can create transactions")
    tx = create_transaction(db, current, payload.user_id, payload.amount, payload.type)
    return TransactionRead.model_validate(tx)

@router.post("/approve", response_model=TransactionRead)
def approve(payload: DebtApprove, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Approve a debt transaction
    WHO CAN USE: CLIENT/USER only
    - Users can approve debt transactions that providers have created for them
    - Only works on PENDING debt transactions
    """
    tx = approve_debt(db, current, payload.transaction_id)
    return TransactionRead.model_validate(tx)

@router.get("/pair/{user_id}/{provider_id}", response_model=list[TransactionRead])
def list_pair(user_id: int, provider_id: int, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    List all transactions between a user and provider
    WHO CAN USE: USER (for their own transactions), PROVIDER (for their transactions), ADMIN (all)
    """
    txs = list_transactions_for_pair(db, current, user_id, provider_id)
    return [TransactionRead.model_validate(tx) for tx in txs]

@router.get("/balance/{user_id}/{provider_id}", response_model=BalanceSummary)
def balance(user_id: int, provider_id: int, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get balance summary between a user and provider
    WHO CAN USE: USER (for their own balance), PROVIDER (for their balances), ADMIN (all)
    """
    summary = compute_balance(db, current, user_id, provider_id)
    return BalanceSummary.model_validate(summary)
