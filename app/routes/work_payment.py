from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.utils.dependencies import get_current_user
from app.models.user import User
from app.schemas.employer import (
    WorkPaymentCreate, 
    WorkPaymentRead, 
    WorkPaymentSummary
)
from app.services.work_payment import (
    create_work_payment,
    get_provider_work_payments,
    get_employer_work_payments,
    get_work_payment,
    update_work_payment,
    delete_work_payment,
    get_work_payment_summary
)

router = APIRouter()


@router.post("/", response_model=WorkPaymentRead)
def add_work_payment(payload: WorkPaymentCreate, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Record a new work payment received from an employer
    WHO CAN USE: PAYER PROVIDER only (contractors)
    - Contractors record payments they received for work done
    """
    work_payment = create_work_payment(
        db, 
        current, 
        payload.employer_id, 
        payload.amount, 
        payload.description,
        payload.payment_date
    )
    
    # Ensure employer relationship is loaded
    db.refresh(work_payment)
    
    # Create response with all required fields
    return WorkPaymentRead(
        id=work_payment.id,
        employer_id=work_payment.employer_id,
        provider_id=work_payment.provider_id,
        amount=work_payment.amount,
        description=work_payment.description,
        payment_date=work_payment.payment_date,
        employer_name=work_payment.employer.name,
        created_at=work_payment.created_at
    )


@router.get("/", response_model=List[WorkPaymentRead])
def get_my_work_payments(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get all work payments for current provider
    WHO CAN USE: PAYER PROVIDER only (contractors)
    - Returns all work payments received from all employers
    """
    work_payments = get_provider_work_payments(db, current)
    
    # Create response with employer names
    result = []
    for payment in work_payments:
        payment_data = WorkPaymentRead(
            id=payment.id,
            employer_id=payment.employer_id,
            provider_id=payment.provider_id,
            amount=payment.amount,
            description=payment.description,
            payment_date=payment.payment_date,
            employer_name=payment.employer.name,
            created_at=payment.created_at
        )
        result.append(payment_data)
    
    return result


@router.get("/employer/{employer_id}", response_model=List[WorkPaymentRead])
def get_payments_from_employer(
    employer_id: int, 
    current: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Get all work payments from a specific employer
    WHO CAN USE: PAYER PROVIDER only (for their employers)
    """
    work_payments = get_employer_work_payments(db, current, employer_id)
    
    # Create response with employer names
    result = []
    for payment in work_payments:
        payment_data = WorkPaymentRead(
            id=payment.id,
            employer_id=payment.employer_id,
            provider_id=payment.provider_id,
            amount=payment.amount,
            description=payment.description,
            payment_date=payment.payment_date,
            employer_name=payment.employer.name,
            created_at=payment.created_at
        )
        result.append(payment_data)
    
    return result


@router.get("/summary", response_model=WorkPaymentSummary)
def get_payment_summary(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get work payment summary statistics
    WHO CAN USE: PAYER PROVIDER only (contractors)
    - Returns total payments, amount, employers count, etc.
    """
    summary = get_work_payment_summary(db, current)
    return WorkPaymentSummary.model_validate(summary)


@router.get("/{payment_id}", response_model=WorkPaymentRead)
def get_work_payment_details(
    payment_id: int, 
    current: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Get details of a specific work payment
    WHO CAN USE: PAYER PROVIDER only (their own payments)
    """
    payment = get_work_payment(db, current, payment_id)
    
    return WorkPaymentRead(
        id=payment.id,
        employer_id=payment.employer_id,
        provider_id=payment.provider_id,
        amount=payment.amount,
        description=payment.description,
        payment_date=payment.payment_date,
        employer_name=payment.employer.name,
        created_at=payment.created_at
    )


@router.put("/{payment_id}", response_model=WorkPaymentRead)
def update_work_payment_record(
    payment_id: int,
    payload: WorkPaymentCreate,  # Reuse create schema for updates
    current: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Update a work payment record
    WHO CAN USE: PAYER PROVIDER only (their own payments)
    """
    # Note: employer_id from payload is ignored, can't change employer
    updated_payment = update_work_payment(
        db,
        current,
        payment_id,
        payload.amount,
        payload.description,
        payload.payment_date
    )
    
    return WorkPaymentRead(
        id=updated_payment.id,
        employer_id=updated_payment.employer_id,
        provider_id=updated_payment.provider_id,
        amount=updated_payment.amount,
        description=updated_payment.description,
        payment_date=updated_payment.payment_date,
        employer_name=updated_payment.employer.name,
        created_at=updated_payment.created_at
    )


@router.delete("/{payment_id}")
def delete_work_payment_record(
    payment_id: int, 
    current: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Delete a work payment record
    WHO CAN USE: PAYER PROVIDER only (their own payments)
    """
    success = delete_work_payment(db, current, payment_id)
    
    if success:
        return {"message": "Work payment deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to delete work payment"
        )