from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, UUID, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
    
class PaymentType(Base):
    __tablename__ = "payment_types"
    
    id = Column('payment_type_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(25), nullable=False)
    code = Column(String(25))
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=True)

    payments = relationship("Payment", back_populates="payment_type")
