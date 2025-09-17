from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base

class LinkStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class UserProvider(Base):
    __tablename__ = "user_provider"
    __table_args__ = (UniqueConstraint('user_id', 'provider_id', name='uq_user_provider'),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(SQLEnum(LinkStatus), default=LinkStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", foreign_keys=[user_id], back_populates="provider_links")
    provider = relationship("User", foreign_keys=[provider_id], back_populates="client_links")
