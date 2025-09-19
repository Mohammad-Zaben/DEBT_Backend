from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.utils.dependencies import get_current_user
from app.models.user import User
from app.schemas.employer import (
    EmployerCreate, 
    EmployerRead, 
    EmployerUpdate
)
from app.services.employer import (
    create_employer,
    get_provider_employers,
    get_employer,
    update_employer,
    delete_employer,
    get_employer_payment_count
)

router = APIRouter()


@router.post("/", response_model=EmployerRead)
def add_employer(payload: EmployerCreate, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Add a new employer
    WHO CAN USE: PAYER PROVIDER only (contractors)
    - Contractors can add employers who pay them for work
    - No approval needed from employer (they don't have accounts)
    """
    employer = create_employer(db, current, payload.name, payload.contact_info)
    
    # Add payment count
    payment_count = get_employer_payment_count(db, employer.id)
    employer_data = EmployerRead.model_validate(employer)
    employer_data.payment_count = payment_count
    
    return employer_data


@router.get("/", response_model=List[EmployerRead])
def get_my_employers(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get all employers for current provider
    WHO CAN USE: PAYER PROVIDER only (contractors)
    - Returns list of all employers with payment counts
    """
    employers = get_provider_employers(db, current)
    
    # Add payment counts to each employer
    result = []
    for employer in employers:
        payment_count = get_employer_payment_count(db, employer.id)
        employer_data = EmployerRead.model_validate(employer)
        employer_data.payment_count = payment_count
        result.append(employer_data)
    
    return result


@router.get("/{employer_id}", response_model=EmployerRead)
def get_employer_details(employer_id: int, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get details of a specific employer
    WHO CAN USE: PAYER PROVIDER only (employers they created)
    """
    employer = get_employer(db, current, employer_id)
    
    # Add payment count
    payment_count = get_employer_payment_count(db, employer.id)
    employer_data = EmployerRead.model_validate(employer)
    employer_data.payment_count = payment_count
    
    return employer_data


@router.put("/{employer_id}", response_model=EmployerRead)
def update_employer_info(
    employer_id: int, 
    payload: EmployerUpdate, 
    current: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Update employer information
    WHO CAN USE: PAYER PROVIDER only (employers they created)
    """
    employer = update_employer(
        db, 
        current, 
        employer_id, 
        payload.name, 
        payload.contact_info
    )
    
    # Add payment count
    payment_count = get_employer_payment_count(db, employer.id)
    employer_data = EmployerRead.model_validate(employer)
    employer_data.payment_count = payment_count
    
    return employer_data


@router.delete("/{employer_id}")
def delete_employer_record(employer_id: int, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Delete an employer
    WHO CAN USE: PAYER PROVIDER only (employers they created)
    - Cannot delete if employer has work payments
    """
    success = delete_employer(db, current, employer_id)
    
    if success:
        return {"message": "Employer deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to delete employer"
        )