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
    
    # Create response with employer name
    result = WorkPaymentRead.model_validate(work_payment)
    result.employer_name = work_payment.employer.name
    
    return result


@router.get("/", response_model=List[WorkPaymentRead])
def get_my_work_payments(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get all work payments for current provider
    WHO CAN USE: PAYER PROVIDER only (contractors)
    - Returns all work payments received from all employers
    """
    work_payments = get_provider_work_payments(db, current)
    
    # Add employer names
    result = []
    for payment in work_payments:
        payment_data = WorkPaymentRead.model_validate(payment)
        payment_data.employer_name = payment.employer.name
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
    
    # Add employer names
    result = []
    for payment in work_payments:
        payment_data = WorkPaymentRead.model_validate(payment)
        payment_data.employer_name = payment.employer.name
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
    
    result = WorkPaymentRead.model_validate(payment)
    result.employer_name = payment.employer.name
    
    return result


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
    
    result = WorkPaymentRead.model_validate(updated_payment)
    result.employer_name = updated_payment.employer.name
    
    return result


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