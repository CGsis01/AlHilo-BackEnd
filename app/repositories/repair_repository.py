from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload, selectinload
from uuid import UUID
from app.models.repair import Repair
from app.models.repair_item import RepairItem
from app.models.repair_item_repair_type import RepairItemRepairType
from app.models.repair_type import RepairType
from app.models.repair_status import RepairStatus
from app.repositories.base import BaseRepository

class RepairRepository(BaseRepository[Repair]):
    def __init__(self, db: AsyncSession):
        super().__init__(Repair, db)

    def _query_with_relations(self):
        return (
            select(Repair).options(
                joinedload(Repair.repair_status),
                joinedload(Repair.created_by_user),
                selectinload(Repair.repair_items).options(
                    joinedload(RepairItem.repair_item_repair_types).joinedload(RepairItemRepairType.repair_type).joinedload(RepairType.repair_complexity),
                    joinedload(RepairItem.repair_status),
                    joinedload(RepairItem.garment),
                    joinedload(RepairItem.assigned_to),
                    joinedload(RepairItem.attended_by))))

    async def get_by_id_with_relations(self, id: UUID) -> Optional[Repair]:
        result = await self.db.execute(
            self._query_with_relations().filter(Repair.id == id))

        return result.unique().scalar_one_or_none()

    async def get_all_filtered(self, filters: Optional[dict] = None) -> List[Repair]:
        query = self._query_with_relations()
        
        if filters:
            assigned_to_id = filters.get("assigned_to_id")
            if assigned_to_id is not None:
                assigned_to_uuid = assigned_to_id if isinstance(assigned_to_id, UUID) else UUID(str(assigned_to_id))
                
                query = query.filter(
                    Repair.repair_items.any(RepairItem.assigned_to_id == assigned_to_uuid))

            for field, value in filters.items():
                if value is None or field == "assigned_to_id":
                    continue

                if hasattr(Repair, field):
                    query = query.filter(getattr(Repair, field) == value)
                elif hasattr(RepairItem, field):
                    query = query.filter(
                        Repair.repair_items.any(getattr(RepairItem, field) == value)
                    )
        
        result = await self.db.execute(query)

        return list(result.scalars().unique().all())

    async def create(self, obj_in: dict) -> Repair:
        db_obj = Repair(**obj_in)

        self.db.add(db_obj)
        
        await self.db.flush()
        
        repair_id = db_obj.id

        await self.db.commit()

        result = await self.db.execute(
            self._query_with_relations().filter(Repair.id == repair_id))

        return result.unique().scalar_one()
    
    async def update(self, id: UUID, obj_in: dict) -> Optional[Repair]:
        result = await self.db.execute(select(self.model).filter(self.model.id == id))

        db_obj = result.scalar_one_or_none()
        
        if db_obj:
            for field, value in obj_in.items():
                if value is not None:
                    setattr(db_obj, field, value)
        
            await self.db.commit()
            await self.db.refresh(db_obj)
        
        result = await self.db.execute(
            self._query_with_relations().filter(Repair.id == id))

        return result.unique().scalar_one()

    async def get_by_client(self, client_id: UUID) -> List[Repair]:
        result = await self.db.execute(
            self._query_with_relations().filter(Repair.client_id == client_id))
        
        return list(result.scalars().unique().all())
    
    async def get_by_status(self, status_id: UUID) -> List[Repair]:
        result = await self.db.execute(
            self._query_with_relations().filter(Repair.repair_status_id == status_id))
        
        return list(result.scalars().unique().all())

    async def get_estimated_time(self) -> int:
        subquery = select(RepairStatus.repair_status_id).where(RepairStatus.name == 'Pendiente').scalar_subquery()
        
        results = await self.db.execute(
            select(func.sum(RepairType.estimated_time))
            .select_from(Repair)
                .join(RepairItem, Repair.id == RepairItem.repair_id)
                .join(RepairItemRepairType, RepairItem.id == RepairItemRepairType.repair_item_id)
                .join(RepairType, RepairItemRepairType.repair_type_id == RepairType.id)
            .where(Repair.repair_status_id == subquery))

        return results.scalar_one_or_none() or 0;
