from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from uuid import UUID
from app.models.repair_comment import RepairComment
from app.models.user import User
from app.repositories.base import BaseRepository

class RepairCommentRepository(BaseRepository[RepairComment]):
    def __init__(self, db: AsyncSession):
        super().__init__(RepairComment, db)

    async def get_by_repair(self, repair_id: UUID) -> List[RepairComment]:
        result = await self.db.execute(
            select(RepairComment)
            .options(
                joinedload(RepairComment.author)
                .joinedload(User.role),
                joinedload(RepairComment.author)
                .joinedload(User.store))
            .filter(RepairComment.repair_id == repair_id)
            .order_by(RepairComment.created_at.desc()))
        
        return list(result.scalars().all())

    async def create_comment(self, obj_in: dict) -> RepairComment:
        data = dict(obj_in)
        db_obj = RepairComment(**data)
        
        self.db.add(db_obj)
        
        await self.db.commit()
        await self.db.refresh(db_obj)

        result = await self.db.execute(
            select(RepairComment)
            .options(
                joinedload(RepairComment.author)
                .joinedload(User.role),
                joinedload(RepairComment.author)
                .joinedload(User.store))
            .filter(RepairComment.id == db_obj.id))
        
        return result.scalar_one()
