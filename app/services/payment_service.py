from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.api_response import ApiResponse
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.repositories.payment_repository import PaymentRepository
from app.schemas.cash_cut import (CardDetail, CashCutMovement, CashCutResponse, PaymentSummary)
from app.repositories.repair_repository import RepairRepository
from decimal import Decimal
from typing import cast

class PaymentService:
    """Service layer for Payment operations"""
    def __init__(self, db: AsyncSession):
        self.db = db
        self.payment_repository = PaymentRepository(db)
        self.repair_repository = RepairRepository(db)

    async def create_payment(self, payment_data: PaymentCreate) -> ApiResponse[PaymentResponse]:
        response = ApiResponse[PaymentResponse](
            status=200,
            message="Payment created successfully",
            code="SUCCESS",
            data=None)

        try:
            payment_dict = payment_data.model_dump()

            payment = await self.payment_repository.create(payment_dict)

            await self.db.commit()

            response.data = PaymentResponse.model_validate(payment)
        except Exception as e:
            await self.db.rollback()
            response.status = 500
            response.message = str(e)
            response.code = "PAYMENT_CREATION_ERROR"
        return response

    async def add_advance_payment(
        self,
        payments_data: List[PaymentCreate]
    ) -> ApiResponse[List[PaymentResponse]]:

        response = ApiResponse[List[PaymentResponse]](
            status=200,
            message="Advance payment created successfully",
            code="SUCCESS",
            data=None
        )

        try:
            if not payments_data:
                response.status = 400
                response.message = "At least one payment is required"
                response.code = "PAYMENT_REQUIRED"
                return response

            repair_id = payments_data[0].repair_id

            if any(payment.repair_id != repair_id for payment in payments_data):
                response.status = 400
                response.message = "All payments must belong to the same repair"
                response.code = "INVALID_REPAIR_PAYMENTS"
                return response

            repair = await self.repair_repository.get_by_id_with_relations(
                repair_id
            )

            if not repair:
                response.status = 404
                response.message = "Repair not found"
                response.code = "REPAIR_NOT_FOUND"
                return response

            advance_payment = cast(
                Decimal | None,
                repair.advance_payment
            )

            if advance_payment is not None and advance_payment > 0:
                response.status = 400
                response.message = "Repair already has an advance payment"
                response.code = "ADVANCE_PAYMENT_ALREADY_EXISTS"
                return response

            if any(payment.amount <= 0 for payment in payments_data):
                response.status = 400
                response.message = "Payment amount must be greater than zero"
                response.code = "INVALID_PAYMENT_AMOUNT"
                return response

            total_advance = sum(
                (
                    Decimal(str(payment.amount))
                    for payment in payments_data
                ),
                Decimal("0")
            )

            created_payments = []

            for payment_data in payments_data:
                payment_dict = payment_data.model_dump()
                payment_dict["is_advance"] = True

                payment = await self.payment_repository.create(
                    payment_dict
                )

                created_payments.append(payment)

            setattr(
                repair,
                "advance_payment",
                total_advance
            )

            await self.db.commit()

            response.data = [
                PaymentResponse.model_validate(payment)
                for payment in created_payments
            ]

        except Exception as e:
            await self.db.rollback()
            response.status = 500
            response.message = str(e)
            response.code = "ADVANCE_PAYMENT_CREATION_ERROR"

        return response

    async def get_payments(self, filters: Optional[dict] = None) -> ApiResponse[List[PaymentResponse]]:
        response = ApiResponse[List[PaymentResponse]](
            status=200,
            message="Payments retrieved successfully",
            code="SUCCESS",
            data=None)
        
        try:
            payments = await self.payment_repository.get_all_filtered(filters)

            if payments is not None:
                response.data = [PaymentResponse.model_validate(payment) for payment in payments]
            
            return response
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "PAYMENT_RETRIEVAL_ERROR"
        
        return response

    async def get_cash_cut(self, cut_date: datetime) -> ApiResponse[CashCutResponse]:
        response = ApiResponse[CashCutResponse](
            status=201,
            message="Cash cut created successfully",
            code="SUCCESS",
            data=None)
        
        try:
            payment_summary = await self.payment_repository.get_cash_cut(cut_date)

            if not payment_summary:
                response.status = 404
                response.message = "No se encontraron movimientos para la fecha especificada"
                response.code = "CASH_CUT_NOT_FOUND"
                return response

            advance_summary = await self.payment_repository.get_cash_cut_by_advance_type(cut_date)
            card_movements = await self.payment_repository.get_card_details(cut_date)
            movements = await self.payment_repository.get_cash_cut_movements(cut_date)

            cash = PaymentSummary(
                name = "Efectivo",
                transactions = 0,
                amount = 0)

            card = PaymentSummary(
                name = "Tarjeta",
                transactions = 0,
                amount = 0)
            
            transfer = PaymentSummary(
                name = "Transferencia",
                transactions = 0,
                amount = 0)

            advances = PaymentSummary(
                name = "Anticipos",
                transactions = 0,
                amount = 0)

            settlements = PaymentSummary(
                name = "Liquidaciones",
                transactions = 0,
                amount = 0)        

            grand_total = 0
            total_transactions = 0

            for payment in payment_summary:
                if payment.name.upper() == "EFECTIVO":
                    cash.transactions = payment.transactions
                    cash.amount = payment.amount

                if payment.name.upper() == "TARJETA":
                    card.transactions = payment.transactions
                    card.amount = payment.amount
                
                if payment.name.upper() == "TRANSFERENCIA":
                    transfer.transactions = payment.transactions
                    transfer.amount = payment.amount

                grand_total += payment.amount
                total_transactions += payment.transactions

            for advance in advance_summary:
                if advance.is_advance:
                    advances.transactions = advance.transactions
                    advances.amount = advance.amount
                else:
                    settlements.transactions = advance.transactions
                    settlements.amount = advance.amount

            response.data = CashCutResponse(
                cash_cut_date = cut_date,
                cash = cash,
                card = card,
                transfer = transfer,
                advances = advances,
                settlements = settlements,
                total_transactions = total_transactions,
                grand_total = grand_total,
                card_details = [CardDetail.model_validate(card) for card in card_movements] if card_movements else [],
                movements = [CashCutMovement.model_validate(movement) for movement in movements])

        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "CASH_CUT_CREATION_ERROR"

        return response