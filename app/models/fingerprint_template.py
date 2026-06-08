from sqlalchemy import Column, DateTime, LargeBinary, SmallInteger, UUID, ForeignKey
from datetime import datetime, timezone
from app.core.database import Base

class UserFingerprintTemplate(Base):
    __tablename__ = "user_fingerprint_templates"

    id = Column("user_fingerprint_template_id", UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    template_index = Column(SmallInteger, nullable=False)
    template_data = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)