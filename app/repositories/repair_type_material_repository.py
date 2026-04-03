from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from app.models.repair_type_material import RepairTypeMaterial
from app.models.repair_type import RepairType
from app.repositories.base import BaseRepository

class RepairTypeMaterialRepository(BaseRepository[RepairTypeMaterial]):
    def __init__(self, db: AsyncSession):
        super().__init__(RepairTypeMaterial, db)

    async def get_by_material_and_repair_type(
        self, 
        material_id: UUID, 
        repair_type_id: UUID, 
        store_id: UUID
    ) -> Optional[RepairTypeMaterial]:
        result = await self.db.execute(
            select(RepairTypeMaterial)
            .options(
                selectinload(RepairTypeMaterial.repair_type).selectinload(RepairType.repair_complexity),
                selectinload(RepairTypeMaterial.material),
                selectinload(RepairTypeMaterial.store))
            .filter(
                and_(
                    RepairTypeMaterial.material_id == material_id,
                    RepairTypeMaterial.repair_type_id == repair_type_id,
                    RepairTypeMaterial.store_id == store_id)))

        return result.scalar_one_or_none()

    async def get_by_repair_type(self, repair_type_id: UUID, store_id: UUID) -> List[RepairTypeMaterial]:
        result = await self.db.execute(
            select(RepairTypeMaterial)
            .options(
                selectinload(RepairTypeMaterial.repair_type).selectinload(RepairType.repair_complexity),
                selectinload(RepairTypeMaterial.material),
                selectinload(RepairTypeMaterial.store))
            .filter(
                and_(
                    RepairTypeMaterial.repair_type_id == repair_type_id,
                    RepairTypeMaterial.store_id == store_id))
            .order_by(RepairTypeMaterial.sort_order))
        
        return list(result.scalars().all())

    async def delete_material_from_repair_type(self, relationship: RepairTypeMaterial) -> bool:
        await self.db.delete(relationship)
        await self.db.commit()
        return True