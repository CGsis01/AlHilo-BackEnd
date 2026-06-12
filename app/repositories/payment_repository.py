from typing import List, Optional
from datetime import date, datetime, time
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload, selectinload
from app.models.payment import Payment
from app.models.payment_type import PaymentType
from app.models.repair import Repair
from app.models.repair_item_repair_type import RepairItemRepairType
from app.models.repair_type import RepairType
from app.models.repair_item import RepairItem
from app.repositories.base import BaseRepository
from app.schemas.cash_cut import AdvanceSummary, CardDetail, CashCutMovement, PaymentSummary

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

    async def get_cash_cut(self, cash_cut_date: date) -> List[PaymentSummary]:
        start_date = datetime.combine(
            cash_cut_date,
            time.min)

        end_date = datetime.combine(
            cash_cut_date,
            time.max)

        query = (
            select(PaymentType.name,
                func.count(Payment.id).label("transactions"),
                func.coalesce(func.sum(Payment.amount), 0).label("amount"))
            .join(PaymentType, Payment.payment_type_id == PaymentType.id)
            .where(
                Payment.created_at >= start_date,
                Payment.created_at <= end_date)
            .group_by(PaymentType.name))

        result = await self.db.execute(query)

        return [PaymentSummary(**row._mapping) for row in result.all()]

    async def get_cash_cut_by_advance_type(self, cash_cut_date: date) -> List[AdvanceSummary]:
        start_date = datetime.combine(
            cash_cut_date,
            time.min)

        end_date = datetime.combine(
            cash_cut_date,
            time.max)

        query = (
            select(Payment.is_advance,
                func.count(Payment.id).label("transactions"),
                func.coalesce(func.sum(Payment.amount), 0).label("amount"))
            .where(
                Payment.created_at >= start_date,
                Payment.created_at <= end_date)
            .group_by(Payment.is_advance))

        result = await self.db.execute(query)

        return [AdvanceSummary(**row._mapping) for row in result.all()]

    async def get_cash_cut_movements(self, cash_cut_date: date) -> List[CashCutMovement]:
        start_date = datetime.combine(
            cash_cut_date,
            time.min)

        end_date = datetime.combine(
            cash_cut_date,
            time.max)

        query = (
            select(Payment.id.label("payment_id"),
                Repair.id.label("repair_id"),
                Repair.customer_name.label("customer_name"),
                PaymentType.name.label("payment_type"),
                Payment.amount.label("amount"),
                Payment.is_advance.label("is_advance"),
                Payment.voucher_id.label("voucher_id"),
                Payment.created_at.label("created_at") )
            .join(Repair, Payment.repair_id == Repair.id)
            .join(PaymentType, Payment.payment_type_id == PaymentType.id)
            .where(
                Payment.created_at >= start_date,
                Payment.created_at <= end_date)
            .order_by(Payment.created_at))

        result = await self.db.execute(query)

        return [CashCutMovement(**row._mapping) for row in result.all()]
    
    async def get_card_details(self, cash_cut_date: date) -> List[CardDetail]:
        start_date = datetime.combine(
            cash_cut_date,
            time.min)

        end_date = datetime.combine(
            cash_cut_date,
            time.max)
        
        query = (
            select(Payment.voucher_id.label("voucher_id"), 
                   Payment.is_debit.label("is_debit"),
                   Payment.amount.label("amount"))
            .join(PaymentType, Payment.payment_type_id == PaymentType.id)
            .where(
                PaymentType.code == "Card",
                Payment.created_at >= start_date,
                Payment.created_at <= end_date)
            .order_by(Payment.created_at))

        result = await self.db.execute(query)

        return [CardDetail(**row._mapping) for row in result.all()]