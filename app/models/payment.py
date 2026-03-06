import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, String, UUID, Numeric, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column('payment_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repair_id = Column(UUID(as_uuid=True), ForeignKey("repairs.repair_id"), nullable=False)
    payment_type_id = Column(UUID(as_uuid=True), ForeignKey("payment_types.payment_type_id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    is_debit = Column(Boolean, default=False, nullable=False)
    voucher_id = Column(String(25))
    is_advance = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    
    repair = relationship("Repair", back_populates="payments")
    payment_type = relationship("PaymentType", back_populates="payments")
    created_by_user = relationship("User", foreign_keys=[created_by], back_populates="created_payments")
