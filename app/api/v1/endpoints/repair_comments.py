from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.schemas.api_response import ApiResponse
from app.schemas.repair_comment import RepairCommentCreate, RepairCommentResponse
from app.services.repair_comment_service import RepairCommentService
from app.api.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=ApiResponse[RepairCommentResponse])
async def add_comment(
    comment_data: RepairCommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    service = RepairCommentService(db)
    return await service.add_comment(comment_data)

@router.get("/{repair_id}", response_model=ApiResponse[List[RepairCommentResponse]])
async def get_comments(
    repair_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    service = RepairCommentService(db)
    return await service.get_comments(repair_id)
