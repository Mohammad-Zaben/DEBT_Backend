from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/init")
def init_otp(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Placeholder endpoint - no real logic yet
    return {"detail": "OTP setup placeholder"}
