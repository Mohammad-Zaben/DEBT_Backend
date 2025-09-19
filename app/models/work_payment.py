from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class WorkPayment(Base):
    __tablename__ = "work_payments"

    id = Column(Integer, primary_key=True, index=True)
    employer_id = Column(Integer, ForeignKey("employers.id", ondelete="CASCADE"), nullable=False)
    provider_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  # Contractor who received payment
    amount = Column(Numeric(12, 2), nullable=False)
    description = Column(Text, nullable=True)  # Work description, project name, etc.
    payment_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    employer = relationship("Employer", back_populates="work_payments")
    provider = relationship("User", back_populates="work_payments")