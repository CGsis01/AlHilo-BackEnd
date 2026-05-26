from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from uuid import UUID
from app.models.repair_item import RepairItem
from app.models.repair_item_repair_type import RepairItemRepairType
from app.models.repair_type import RepairType
from app.models.garment import Garment
from app.models.repair_status import RepairStatus
from app.repositories.base import BaseRepository

class RepairItemRepository(BaseRepository[RepairItem]):
    def __init__(self, db: AsyncSession):
        super().__init__(RepairItem, db)

    async def _get_status_id_by_name(self, status_name: str) -> Optional[UUID]:
        result = await self.db.execute(select(RepairStatus.repair_status_id).filter(RepairStatus.name == status_name))

        return result.scalar_one_or_none()

    def _query_with_relations(self):
        return (
            select(RepairItem).options(
                joinedload(RepairItem.repair_item_repair_types).joinedload(RepairItemRepairType.repair_type).joinedload(RepairType.repair_complexity),
                joinedload(RepairItem.repair_status),
                joinedload(RepairItem.garment),
                joinedload(RepairItem.assigned_to)
            )
        )

    async def get_by_id_with_relations(self, id: UUID) -> Optional[RepairItem]:
        result = await self.db.execute(
            self._query_with_relations().filter(RepairItem.id == id))
        
        return result.unique().scalar_one_or_none()

    async def get_by_repair_id(self, repair_id: UUID) -> List[RepairItem]:
        result = await self.db.execute(
            self._query_with_relations().filter(RepairItem.repair_id == repair_id))
        
        return list(result.scalars().unique().all())

    async def get_by_assigned_to(self, assigned_to_id: UUID) -> List[RepairItem]:
        """Get all repair items assigned to a seamstress"""
        result = await self.db.execute(
            self._query_with_relations().filter(RepairItem.assigned_to_id == assigned_to_id))
        
        return list(result.scalars().unique().all())

    async def assign(self, repair_item_id: UUID, assigned_to_id: Optional[UUID]) -> Optional[RepairItem]:
        """Assign or unassign a repair item to a seamstress"""
        result = await self.db.execute(select(self.model).filter(self.model.id == repair_item_id))
        
        db_obj = result.scalar_one_or_none()
        
        if db_obj:
            in_progress_status_id = await self._get_status_id_by_name("En progreso")
            pending_status_id = await self._get_status_id_by_name("Pendiente")

            setattr(db_obj, 'assigned_to_id', assigned_to_id)
            setattr(db_obj, 'attended_by_id', assigned_to_id)
            
            target_status_id = in_progress_status_id if assigned_to_id else pending_status_id
            
            if target_status_id:
                setattr(db_obj, 'repair_status_id', target_status_id)

            await self.db.commit()
            await self.db.refresh(db_obj)
            
            # Reload with relations
            return await self.get_by_id_with_relations(repair_item_id)
        
        return None

    async def assign_bulk(self, assignments: dict[UUID, Optional[UUID]]) -> List[RepairItem]:
        """Bulk assign/unassign multiple repair items"""
        updated_items = []
        in_progress_status_id = await self._get_status_id_by_name("En progreso")
        pending_status_id = await self._get_status_id_by_name("Pendiente")
        
        for repair_item_id, assigned_to_id in assignments.items():
            result = await self.db.execute(select(self.model).filter(self.model.id == repair_item_id))
            
            db_obj = result.scalar_one_or_none()
            
            if db_obj:
                setattr(db_obj, 'assigned_to_id', assigned_to_id)
                setattr(db_obj, 'attended_by_id', assigned_to_id) 

                target_status_id = in_progress_status_id if assigned_to_id else pending_status_id
                
                if target_status_id:
                    setattr(db_obj, 'repair_status_id', target_status_id)

                updated_items.append(db_obj)
        
        if updated_items:
            await self.db.commit()
            
            # Reload with relations
            updated_with_relations = []
            for item_id in assignments.keys():
                item = await self.get_by_id_with_relations(item_id)
                if item:
                    updated_with_relations.append(item)
            
            return updated_with_relations
        
        return []

    async def update_status(self, repair_item_id: UUID, repair_status_id: UUID) -> Optional[RepairItem]:
        result = await self.db.execute(select(self.model).filter(self.model.id == repair_item_id))
        db_obj = result.scalar_one_or_none()

        if db_obj:
            status_result = await self.db.execute(select(RepairStatus.name).filter(RepairStatus.repair_status_id == repair_status_id))
            target_status_name = status_result.scalar_one_or_none()

            setattr(db_obj, 'repair_status_id', repair_status_id)
            
            if target_status_name == "Validada":
                setattr(db_obj, 'assigned_to_id', None)
            
            await self.db.commit()
            await self.db.refresh(db_obj)

            return await self.get_by_id_with_relations(repair_item_id)

        return None
