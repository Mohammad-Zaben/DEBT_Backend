from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.models.user import User, UserRole, ProviderType
from app.models.employer import Employer
from app.models.work_payment import WorkPayment


def create_employer(db: Session, provider: User, name: str, contact_info: Optional[str] = None) -> Employer:
    """Create a new employer for a PAYER provider"""
    # Only PAYER providers can add employers
    if provider.role != UserRole.PROVIDER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only providers can add employers"
        )
    
    if provider.provider_type != ProviderType.PAYER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only PAYER providers (contractors) can add employers"
        )
    
    # Check for duplicate employer name for this provider
    existing = db.query(Employer).filter(
        Employer.created_by == provider.id,
        Employer.name == name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Employer with this name already exists"
        )
    
    employer = Employer(
        name=name,
        contact_info=contact_info,
        created_by=provider.id
    )
    db.add(employer)
    db.commit()
    db.refresh(employer)
    return employer


def get_provider_employers(db: Session, provider: User) -> List[Employer]:
    """Get all employers for a provider with payment counts"""
    if provider.role != UserRole.PROVIDER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only providers can access employers"
        )
    
    if provider.provider_type != ProviderType.PAYER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only PAYER providers can access employers"
        )
    
    return db.query(Employer).filter(Employer.created_by == provider.id).all()


def get_employer(db: Session, provider: User, employer_id: int) -> Employer:
    """Get a specific employer by ID"""
    employer = db.query(Employer).filter(
        Employer.id == employer_id,
        Employer.created_by == provider.id
    ).first()
    
    if not employer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Employer not found"
        )
    
    return employer


def update_employer(
    db: Session, 
    provider: User, 
    employer_id: int, 
    name: Optional[str] = None, 
    contact_info: Optional[str] = None
) -> Employer:
    """Update employer information"""
    employer = get_employer(db, provider, employer_id)
    
    if name is not None:
        # Check for duplicate name
        existing = db.query(Employer).filter(
            Employer.created_by == provider.id,
            Employer.name == name,
            Employer.id != employer_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Employer with this name already exists"
            )
        
        employer.name = name
    
    if contact_info is not None:
        employer.contact_info = contact_info
    
    db.commit()
    db.refresh(employer)
    return employer


def delete_employer(db: Session, provider: User, employer_id: int) -> bool:
    """Delete an employer (and all related work payments)"""
    employer = get_employer(db, provider, employer_id)
    
    # Check if there are work payments
    payment_count = db.query(WorkPayment).filter(WorkPayment.employer_id == employer_id).count()
    
    if payment_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Cannot delete employer with {payment_count} work payments. Delete payments first."
        )
    
    db.delete(employer)
    db.commit()
    return True


def get_employer_payment_count(db: Session, employer_id: int) -> int:
    """Get the number of work payments for an employer"""
    return db.query(WorkPayment).filter(WorkPayment.employer_id == employer_id).count()