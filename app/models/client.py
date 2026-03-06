import uuid
from sqlalchemy import Column, String, UUID, Text, Date
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Client(BaseModel):
    __tablename__ = "clients"
    
    id = Column('client_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(255), nullable=False, index=True)
    address = Column(Text, nullable=False)
    personal_phone = Column(String(20), nullable=False, index=True)
    contact_phone = Column(String(20), nullable=False, index=True)
    email = Column(String(255), index=True)
    facebook = Column(String(255))
    instagram = Column(String(255))
    birth_date = Column(Date)
    
    repairs = relationship("Repair", back_populates="client")
