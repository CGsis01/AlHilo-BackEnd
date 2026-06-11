from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.api_response import ApiResponse
from app.schemas.cash_cut import CashCutResponse
from app.services.payment_service import PaymentService

router = APIRouter()

@router.get("/", response_model=ApiResponse[CashCutResponse])
async def get_cash_cut(
    cash_cut_date: datetime,
    db: AsyncSession = Depends(get_db)) -> ApiResponse[CashCutResponse]:
    service = PaymentService(db)

    return await service.get_cash_cut(cash_cut_date)