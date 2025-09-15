from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base

class UserRole(str, enum.Enum):
    USER = "User"
    PROVIDER = "Provider"
    ADMIN = "Admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    provider_links = relationship("UserProvider", foreign_keys="UserProvider.user_id", back_populates="user", cascade="all, delete-orphan")
    client_links = relationship("UserProvider", foreign_keys="UserProvider.provider_id", back_populates="provider", cascade="all, delete-orphan")
    user_transactions = relationship("Transaction", foreign_keys="Transaction.user_id", back_populates="user")
    provider_transactions = relationship("Transaction", foreign_keys="Transaction.provider_id", back_populates="provider")
    otp = relationship("OTP", uselist=False, back_populates="user")
