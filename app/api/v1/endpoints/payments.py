from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from app.core.database import get_db
from app.schemas.api_response import ApiResponse
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services.payment_service import PaymentService
from app.api.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=ApiResponse[PaymentResponse])
async def create_payment(
    payment_data: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    payment_service = PaymentService(db)
    
    return await payment_service.create_payment(payment_data)

@router.get("/", response_model=ApiResponse[List[PaymentResponse]])
async def get_payments(
    repair_id: Optional[UUID] = Query(None, description="Filter by repair ID"),
    client_id: Optional[UUID] = Query(None, description="Filter by client ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    payment_service = PaymentService(db)

    filters = {}
    if repair_id:
        filters['repair_id'] = repair_id
    if client_id:
        filters['client_id'] = client_id
    
    return await payment_service.get_payments(filters)