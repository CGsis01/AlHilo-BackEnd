from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class BaseModel(Base):
    """Base model for all entities matching .NET BaseEntity"""
    __abstract__ = True
    
    # Don't define id here - let each model define its own with proper column name
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
