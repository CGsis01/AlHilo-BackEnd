from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.payment_type_repository import PaymentTypeRepository
from app.schemas.api_response import ApiResponse
from app.schemas.payment_type import PaymentTypeResponse

class PaymentTypeService:
    """Service layer for PaymentType operations"""
    def __init__(self, db: AsyncSession):
        self.db = db
        self.payment_type_repository = PaymentTypeRepository(db)

    async def get_payment_types(self) -> ApiResponse[List[PaymentTypeResponse]]:
        response = ApiResponse[List[PaymentTypeResponse]](
            status=200,
            message="Payment types retrieved successfully",
            code="SUCCESS",
            data=None)
        
        try:
            payment_types = await self.payment_type_repository.get_all()

            if payment_types is not None:
                response.data = [PaymentTypeResponse.model_validate(payment_type) for payment_type in payment_types]
            
            return response
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "PAYMENT_TYPE_RETRIEVAL_ERROR"
        
        return response
