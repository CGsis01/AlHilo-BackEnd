from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.api_response import ApiResponse
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.repositories.payment_repository import PaymentRepository

class PaymentService:
    """Service layer for Payment operations"""
    def __init__(self, db: AsyncSession):
        self.db = db
        self.payment_repository = PaymentRepository(db)

    async def create_payment(self, payment_data: PaymentCreate) -> ApiResponse[PaymentResponse]:
        response = ApiResponse[PaymentResponse](
            status=200,
            message="Payment created successfully",
            code="SUCCESS",
            data=None)

        try:
            payment_dict = payment_data.model_dump()

            payment = await self.payment_repository.create(payment_dict)

            response.data = PaymentResponse.model_validate(payment)
        except Exception as e:
            await self.db.rollback()
            response.status = 500
            response.message = str(e)
            response.code = "PAYMENT_CREATION_ERROR"
        
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
