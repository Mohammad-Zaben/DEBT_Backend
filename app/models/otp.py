from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

# Placeholder OTP model (future expansion for TOTP secret storage)
class OTP(Base):
    __tablename__ = "otp"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    secret = Column(String, unique=True, nullable=False)
    code = Column(String, nullable=True)  # transient storage if needed
    expiry_time = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="otp")
