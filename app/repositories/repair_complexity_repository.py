from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.repair_complexity import RepairComplexity
from app.repositories.base import BaseRepository

class RepairComplexityRepository(BaseRepository[RepairComplexity]):
    def __init__(self, db: AsyncSession):
        super().__init__(RepairComplexity, db)

    async def deactivate_repair_complexity(self, repair_complexity_id: UUID, user_id: UUID) -> Optional[RepairComplexity]:
        result = await self.db.execute(select(RepairComplexity).filter(RepairComplexity.id == repair_complexity_id))
        repair_complexity = result.scalar_one_or_none()

        if repair_complexity:
            setattr(repair_complexity, "is_active", False)
            setattr(repair_complexity, "updated_by", user_id)

            await self.db.commit()
            await self.db.refresh(repair_complexity)

        return repair_complexity

    async def activate_repair_complexity(self, repair_complexity_id: UUID, user_id: UUID) -> Optional[RepairComplexity]:
        result = await self.db.execute(select(RepairComplexity).filter(RepairComplexity.id == repair_complexity_id))
        repair_complexity = result.scalar_one_or_none()

        if repair_complexity:
            setattr(repair_complexity, "is_active", True)
            setattr(repair_complexity, "updated_by", user_id)

            await self.db.commit()
            await self.db.refresh(repair_complexity)

        return repair_complexity

    async def get_by_store(self, store_id: UUID) -> List[RepairComplexity]:
        """Get all repair complexities for a specific store"""
        result = await self.db.execute(
            select(RepairComplexity)
            .filter(RepairComplexity.store_id == store_id)
            .order_by(RepairComplexity.name)
        )
        return list(result.scalars().all())
