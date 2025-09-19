from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from typing import List, Optional
from app.models.user import User, UserRole, ProviderType
from app.models.employer import Employer
from app.models.work_payment import WorkPayment


def create_work_payment(
    db: Session, 
    provider: User, 
    employer_id: int, 
    amount: Decimal, 
    description: Optional[str] = None,
    payment_date: Optional[datetime] = None
) -> WorkPayment:
    """Create a new work payment received from an employer"""
    # Only PAYER providers can add work payments
    if provider.role != UserRole.PROVIDER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only providers can add work payments"
        )
    
    if provider.provider_type != ProviderType.PAYER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only PAYER providers (contractors) can add work payments"
        )
    
    # Verify employer exists and belongs to this provider
    employer = db.query(Employer).filter(
        Employer.id == employer_id,
        Employer.created_by == provider.id
    ).first()
    
    if not employer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Employer not found"
        )
    
    # Validate amount
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Payment amount must be greater than 0"
        )
    
    work_payment = WorkPayment(
        employer_id=employer_id,
        provider_id=provider.id,
        amount=amount,
        description=description,
        payment_date=payment_date or datetime.utcnow()
    )
    
    db.add(work_payment)
    db.commit()
    db.refresh(work_payment)
    
    # Load the employer relationship
    work_payment = db.query(WorkPayment).options(joinedload(WorkPayment.employer)).filter(
        WorkPayment.id == work_payment.id
    ).first()
    
    return work_payment


def get_provider_work_payments(db: Session, provider: User) -> List[WorkPayment]:
    """Get all work payments for a provider"""
    if provider.role != UserRole.PROVIDER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only providers can access work payments"
        )
    
    if provider.provider_type != ProviderType.PAYER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only PAYER providers can access work payments"
        )
    
    return db.query(WorkPayment).options(joinedload(WorkPayment.employer)).filter(
        WorkPayment.provider_id == provider.id
    ).order_by(desc(WorkPayment.payment_date)).all()


def get_employer_work_payments(db: Session, provider: User, employer_id: int) -> List[WorkPayment]:
    """Get all work payments from a specific employer"""
    # Verify employer belongs to this provider
    employer = db.query(Employer).filter(
        Employer.id == employer_id,
        Employer.created_by == provider.id
    ).first()
    
    if not employer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Employer not found"
        )
    
    return db.query(WorkPayment).options(joinedload(WorkPayment.employer)).filter(
        WorkPayment.employer_id == employer_id,
        WorkPayment.provider_id == provider.id
    ).order_by(desc(WorkPayment.payment_date)).all()


def get_work_payment(db: Session, provider: User, payment_id: int) -> WorkPayment:
    """Get a specific work payment"""
    payment = db.query(WorkPayment).options(joinedload(WorkPayment.employer)).filter(
        WorkPayment.id == payment_id,
        WorkPayment.provider_id == provider.id
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Work payment not found"
        )
    
    return payment


def update_work_payment(
    db: Session, 
    provider: User, 
    payment_id: int, 
    amount: Optional[Decimal] = None,
    description: Optional[str] = None,
    payment_date: Optional[datetime] = None
) -> WorkPayment:
    """Update a work payment"""
    payment = get_work_payment(db, provider, payment_id)
    
    if amount is not None:
        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Payment amount must be greater than 0"
            )
        payment.amount = amount
    
    if description is not None:
        payment.description = description
        
    if payment_date is not None:
        payment.payment_date = payment_date
    
    db.commit()
    db.refresh(payment)
    
    # Reload with employer relationship
    payment = db.query(WorkPayment).options(joinedload(WorkPayment.employer)).filter(
        WorkPayment.id == payment.id
    ).first()
    
    return payment


def delete_work_payment(db: Session, provider: User, payment_id: int) -> bool:
    """Delete a work payment"""
    payment = get_work_payment(db, provider, payment_id)
    
    db.delete(payment)
    db.commit()
    return True


def get_work_payment_summary(db: Session, provider: User) -> dict:
    """Get summary statistics for provider's work payments"""
    if provider.role != UserRole.PROVIDER or provider.provider_type != ProviderType.PAYER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only PAYER providers can access work payment summary"
        )
    
    # Get totals
    payment_stats = db.query(
        func.count(WorkPayment.id).label('total_payments'),
        func.coalesce(func.sum(WorkPayment.amount), 0).label('total_amount'),
        func.max(WorkPayment.payment_date).label('last_payment_date')
    ).filter(WorkPayment.provider_id == provider.id).first()
    
    # Get unique employers count
    employers_count = db.query(func.count(func.distinct(Employer.id))).filter(
        Employer.created_by == provider.id
    ).scalar()
    
    return {
        "total_payments": payment_stats.total_payments or 0,
        "total_amount": payment_stats.total_amount or 0,
        "employers_count": employers_count or 0,
        "last_payment_date": payment_stats.last_payment_date
    }