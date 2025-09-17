from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.models.user import User, UserRole, ProviderType
from app.models.user_provider import UserProvider


def _check_link_exists(db: Session, user_id: int, provider_id: int):
    return db.query(UserProvider).filter(UserProvider.user_id == user_id, UserProvider.provider_id == provider_id).first()


def create_transaction(db: Session, provider: User, user_id: int, amount: Decimal, t_type: TransactionType):
    # Provider must be provider role
    if provider.role != UserRole.PROVIDER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only providers can create transactions")
    
    # Provider type validation: PAYER providers can only create PAYMENT transactions
    if provider.provider_type == ProviderType.PAYER and t_type == TransactionType.DEBT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Payer providers can only record payments, not debts. Only lender providers can add debts."
        )
    
    # Link must exist
    if not _check_link_exists(db, user_id, provider.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Link does not exist")

    status_value = TransactionStatus.PENDING if t_type == TransactionType.DEBT else TransactionStatus.CONFIRMED
    tx = Transaction(user_id=user_id, provider_id=provider.id, type=t_type, amount=amount, status=status_value)
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


def approve_debt(db: Session, client: User, transaction_id: int):
    tx = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.user_id == client.id).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    if tx.type != TransactionType.DEBT or tx.status != TransactionStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transaction not pending debt")
    # Future: Verify OTP here
    tx.status = TransactionStatus.CONFIRMED
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


def list_transactions_for_pair(db: Session, requester: User, user_id: int, provider_id: int):
    # Authorization: requester must be either the user (client) or the provider
    if requester.role == UserRole.USER and requester.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    if requester.role == UserRole.PROVIDER and requester.id != provider_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    if requester.role == UserRole.ADMIN:
        pass
    # Ensure link exists (except admin maybe) when not admin
    if requester.role != UserRole.ADMIN and not _check_link_exists(db, user_id, provider_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Link does not exist")
    return db.query(Transaction).filter(Transaction.user_id == user_id, Transaction.provider_id == provider_id).all()


def compute_balance(db: Session, requester: User, user_id: int, provider_id: int):
    # Authorization same as list
    if requester.role == UserRole.USER and requester.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    if requester.role == UserRole.PROVIDER and requester.id != provider_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    if requester.role != UserRole.ADMIN and not _check_link_exists(db, user_id, provider_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Link does not exist")

    confirmed = db.query(Transaction).filter(Transaction.user_id == user_id, Transaction.provider_id == provider_id, Transaction.status == TransactionStatus.CONFIRMED)
    debt_total = confirmed.filter(Transaction.type == TransactionType.DEBT).with_entities(func.coalesce(func.sum(Transaction.amount), 0)).scalar()  # type: ignore
    payment_total = confirmed.filter(Transaction.type == TransactionType.PAYMENT).with_entities(func.coalesce(func.sum(Transaction.amount), 0)).scalar()  # type: ignore
    balance = (debt_total or 0) - (payment_total or 0)
    return {
        "user_id": user_id,
        "provider_id": provider_id,
        "total_debt": debt_total or 0,
        "total_payments": payment_total or 0,
        "balance": balance
    }
