from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Employer(Base):
    __tablename__ = "employers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact_info = Column(Text, nullable=True)  # Phone, email, address, etc.
    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  # Provider who added this employer
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    provider = relationship("User", back_populates="employers")
    work_payments = relationship("WorkPayment", back_populates="employer", cascade="all, delete-orphan")