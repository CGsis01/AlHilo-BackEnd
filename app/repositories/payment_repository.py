from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from app.models.payment import Payment
from app.models.repair import Repair
from app.models.repair_item_repair_type import RepairItemRepairType
from app.models.repair_type import RepairType
from app.models.repair_item import RepairItem
from app.repositories.base import BaseRepository

class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, db: AsyncSession):
        super().__init__(Payment, db)

    def _query_with_relations(self):
        return (
            select(Payment).options(
                joinedload(Payment.repair).joinedload(Repair.repair_status),
                joinedload(Payment.repair).joinedload(Repair.created_by_user),
                joinedload(Payment.repair).selectinload(
                    Repair.repair_items).options(
                    selectinload(RepairItem.garment),
                    selectinload(RepairItem.repair_item_repair_types).selectinload(RepairItemRepairType.repair_type).selectinload(RepairType.repair_complexity),
                    selectinload(RepairItem.assigned_to),
                    selectinload(RepairItem.attended_by),
                ),
                joinedload(Payment.payment_type),
                joinedload(Payment.created_by_user),
            )
        )

    async def get_all_filtered(self, filters: Optional[dict] = None) -> List[Payment]:
        query = self._query_with_relations()
        
        if filters:
            for field, value in filters.items():
                if value is not None:
                    query = query.filter(getattr(Payment, field) == value)
        
        result = await self.db.execute(query)

        return list(result.scalars().unique().all())

    async def create(self, obj_in: dict) -> Payment:
        db_obj = Payment(**obj_in)

        self.db.add(db_obj)
        
        await self.db.flush()
        
        payment_id = db_obj.id

        await self.db.commit()

        result = await self.db.execute(
            self._query_with_relations().filter(Payment.id == payment_id))

        return result.unique().scalar_one()
