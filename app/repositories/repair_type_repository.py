from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.repair_type import RepairType
from app.repositories.base import BaseRepository

class RepairTypeRepository(BaseRepository[RepairType]):
    def __init__(self, db: AsyncSession):
        super().__init__(RepairType, db)

    async def get_by_id(self, id: UUID, store_id: Optional[UUID] = None) -> Optional[RepairType]:
        """Override to eagerly load relationships"""
        query = select(RepairType).filter(RepairType.id == id).options(
            selectinload(RepairType.repair_complexity),
            selectinload(RepairType.store)
        )
        
        if store_id is not None:
            query = query.filter(RepairType.store_id == store_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, obj_in: dict) -> RepairType:
        """Override to eagerly load relationships after creation"""
        db_obj = RepairType(**obj_in)
        self.db.add(db_obj)
        await self.db.commit()
        
        # Reload with relationships
        result = await self.db.execute(
            select(RepairType)
            .filter(RepairType.id == db_obj.id)
            .options(
                selectinload(RepairType.repair_complexity),
                selectinload(RepairType.store)
            )
        )
        return result.scalar_one()

    async def update(self, id: UUID, obj_in: dict) -> Optional[RepairType]:
        """Override to eagerly load relationships after update"""
        result = await self.db.execute(select(RepairType).filter(RepairType.id == id))
        db_obj = result.scalar_one_or_none()
        
        if db_obj:
            for field, value in obj_in.items():
                if value is not None:
                    setattr(db_obj, field, value)
            
            await self.db.commit()
            
            # Reload with relationships
            result = await self.db.execute(
                select(RepairType)
                .filter(RepairType.id == id)
                .options(
                    selectinload(RepairType.repair_complexity),
                    selectinload(RepairType.store)
                )
            )
            return result.scalar_one()
        
        return db_obj

    async def get_all_with_relationships(self, store_id: Optional[UUID] = None) -> Optional[list[RepairType]]:
        query = select(RepairType).options(
            selectinload(RepairType.repair_complexity),
            selectinload(RepairType.store)
        )
        
        if store_id is not None:
            query = query.filter(RepairType.store_id == store_id)
        
        result = await self.db.execute(query)
        
        return list(result.scalars().all())
    
    async def deactivate_repair_type(self, repair_type_id: UUID, store_id: UUID, user_id: UUID) -> Optional[RepairType]:
        result = await self.db.execute(select(RepairType).filter(RepairType.id == repair_type_id, RepairType.store_id == store_id))
        repair_type = result.scalar_one_or_none()

        if repair_type:
            setattr(repair_type, "is_active", False)
            setattr(repair_type, "updated_by", user_id)

            await self.db.commit()
            await self.db.refresh(repair_type)

        return repair_type

    async def activate_repair_type(self, repair_type_id: UUID, store_id: UUID, user_id: UUID) -> Optional[RepairType]:
        result = await self.db.execute(select(RepairType).filter(RepairType.id == repair_type_id, RepairType.store_id == store_id))
        repair_type = result.scalar_one_or_none()

        if repair_type:
            setattr(repair_type, "is_active", True)
            setattr(repair_type, "updated_by", user_id)

            await self.db.commit()
            await self.db.refresh(repair_type)

        return repair_type