from fastapi import APIRouter, Depends
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.schemas.api_response import ApiResponse
from app.schemas.store import StoreCreate, StoreUpdate, StoreResponse, StoreDeactivate, StoreActivate
from app.services.store_service import StoreService
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=ApiResponse[StoreResponse])
async def create_store(
    store_data: StoreCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    store_service = StoreService(db)
    
    return await store_service.create_store(store_data)

@router.put("/deactivate", response_model=ApiResponse[bool])
async def deactivate_store(
    store_data: StoreDeactivate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    store_service = StoreService(db)
    
    return await store_service.deactivate_store(store_data)

@router.put("/activate", response_model=ApiResponse[bool])
async def activate_store(
    store_data: StoreActivate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    store_service = StoreService(db)
    
    return await store_service.activate_store(store_data)

@router.put("/{store_id}", response_model=ApiResponse[StoreResponse])
async def update_store(
    store_id: UUID,
    store_data: StoreUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    store_service = StoreService(db)

    return await store_service.update_store(store_id, store_data)

@router.get("/", response_model=ApiResponse[List[StoreResponse]])
async def get_stores(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)) -> ApiResponse[List[StoreResponse]]:
    store_service = StoreService(db)

    return await store_service.get_stores()
