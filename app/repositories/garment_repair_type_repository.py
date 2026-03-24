from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from app.models.garment_repair_type import GarmentRepairType
from app.models.repair_type import RepairType
from app.repositories.base import BaseRepository

class GarmentRepairTypeRepository(BaseRepository[GarmentRepairType]):
    def __init__(self, db: AsyncSession):
        super().__init__(GarmentRepairType, db)

    async def get_by_garment_and_repair_type(
        self, 
        garment_id: UUID, 
        repair_type_id: UUID, 
        store_id: UUID
    ) -> Optional[GarmentRepairType]:
        result = await self.db.execute(
            select(GarmentRepairType)
            .options(selectinload(GarmentRepairType.repair_type))
            .filter(
                and_(
                    GarmentRepairType.garment_id == garment_id,
                    GarmentRepairType.repair_type_id == repair_type_id,
                    GarmentRepairType.store_id == store_id)))
        
        return result.scalar_one_or_none()

    async def get_by_garment(self, garment_id: UUID, store_id: UUID) -> List[GarmentRepairType]:
        result = await self.db.execute(
            select(GarmentRepairType)
            .options(selectinload(GarmentRepairType.repair_type))
            .filter(
                and_(
                    GarmentRepairType.garment_id == garment_id,
                    GarmentRepairType.store_id == store_id,
                    GarmentRepairType.is_active == True))
            .order_by(GarmentRepairType.sort_order))
        
        return list(result.scalars().all())

    async def deactivate(
        self, 
        garment_id: UUID, 
        repair_type_id: UUID, 
        store_id: UUID, 
        user_id: UUID
    ) -> Optional[GarmentRepairType]:
        garment_repair_type = await self.get_by_garment_and_repair_type(
            garment_id, 
            repair_type_id, 
            store_id)

        if garment_repair_type:
            setattr(garment_repair_type, "is_active", False)
            setattr(garment_repair_type, "updated_by", user_id)

            await self.db.commit()
            await self.db.refresh(garment_repair_type)

        return garment_repair_type

    async def activate(
        self, 
        garment_id: UUID, 
        repair_type_id: UUID, 
        store_id: UUID, 
        user_id: UUID
    ) -> Optional[GarmentRepairType]:
        garment_repair_type = await self.get_by_garment_and_repair_type(
            garment_id, 
            repair_type_id, 
            store_id)

        if garment_repair_type:
            setattr(garment_repair_type, "is_active", True)
            setattr(garment_repair_type, "updated_by", user_id)

            await self.db.commit()
            await self.db.refresh(garment_repair_type)

        return garment_repair_type

    async def update_relationship(
        self,
        garment_id: UUID,
        repair_type_id: UUID,
        store_id: UUID,
        update_data: dict
    ) -> Optional[GarmentRepairType]:
        garment_repair_type = await self.get_by_garment_and_repair_type(
            garment_id,
            repair_type_id,
            store_id)

        if garment_repair_type:
            for key, value in update_data.items():
                if hasattr(garment_repair_type, key) and value is not None:
                    setattr(garment_repair_type, key, value)

            await self.db.commit()
            await self.db.refresh(garment_repair_type, ["repair_type"])

        return garment_repair_type
