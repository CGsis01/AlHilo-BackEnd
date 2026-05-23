import uuid
from sqlalchemy import Column, UUID, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class RepairComment(BaseModel):
    __tablename__ = "repair_comments"

    id = Column('repair_comment_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repair_id = Column(UUID(as_uuid=True), ForeignKey("repairs.repair_id"), nullable=False)
    comment = Column(Text, nullable=False)
    updated_comment = Column('updatedComment', Text)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)

    repair = relationship("Repair", back_populates="comments")
    author = relationship("User", foreign_keys="[RepairComment.created_by]", lazy="select")
