from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.schemas.api_response import ApiResponse
from app.schemas.payment_type import PaymentTypeResponse
from app.services.payment_type_service import PaymentTypeService
from app.api.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=ApiResponse[List[PaymentTypeResponse]])
async def get_payment_types(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> ApiResponse[List[PaymentTypeResponse]]:
    payment_type_service = PaymentTypeService(db)
    
    return await payment_type_service.get_payment_types()
