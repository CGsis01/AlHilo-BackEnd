from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.schemas.api_response import ApiResponse
from app.schemas.garment import (
    GarmentCreate, 
    GarmentUpdate, 
    GarmentResponse, 
    GarmentDeactivate, 
    GarmentActivate)
from app.schemas.garment_repair_type import (
    GarmentRepairTypeCreate,
    GarmentRepairTypeUpdate,
    GarmentRepairTypeResponse,
    GarmentRepairTypeActivate,
    GarmentRepairTypeDeactivate)
from app.services.garment_service import GarmentService
from app.services.garment_repair_type_service import GarmentRepairTypeService
from app.models.user import User

router = APIRouter()

# ========== Garment Endpoints ==========

@router.post("/", response_model=ApiResponse[GarmentResponse])
async def create_garment(
    garment_data: GarmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    garment_service = GarmentService(db)
    
    return await garment_service.create_garment(garment_data)

@router.put("/deactivate", response_model=ApiResponse[bool])
async def deactivate_garment(
    garment_data: GarmentDeactivate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    garment_service = GarmentService(db)
    
    return await garment_service.deactivate_garment(garment_data)

@router.put("/activate", response_model=ApiResponse[bool])
async def activate_garment(
    garment_data: GarmentActivate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    garment_service = GarmentService(db)
    
    return await garment_service.activate_garment(garment_data)

@router.put("/{garment_id}", response_model=ApiResponse[GarmentResponse])
async def update_garment(
    garment_id: UUID,
    garment_data: GarmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    garment_service = GarmentService(db)
    
    return await garment_service.update_garment(garment_id, garment_data)

@router.get("/", response_model=ApiResponse[List[GarmentResponse]])
async def get_garments(
    store_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)) -> ApiResponse[List[GarmentResponse]]:
    garment_service = GarmentService(db)

    return await garment_service.get_garments(store_id)

@router.get("/{garment_id}", response_model=ApiResponse[GarmentResponse])
async def get_garment_by_id(
    garment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    garment_service = GarmentService(db)
    
    return await garment_service.get_garment_by_id(garment_id)

# ========== Garment Repair Type Relationship Endpoints ==========

@router.post("/{garment_id}/repair-types", response_model=ApiResponse[GarmentRepairTypeResponse])
async def add_repair_type_to_garment(
    garment_id: UUID,
    relationship_data: GarmentRepairTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    garment_repair_type_service = GarmentRepairTypeService(db)
    
    return await garment_repair_type_service.add_repair_type_to_garment(relationship_data)

@router.get("/{garment_id}/repair-types", response_model=ApiResponse[List[GarmentRepairTypeResponse]])
async def get_garment_repair_types(
    garment_id: UUID,
    store_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    garment_repair_type_service = GarmentRepairTypeService(db)
    
    return await garment_repair_type_service.get_garment_repair_types(garment_id, store_id)

@router.put("/{garment_id}/repair-types/{repair_type_id}", response_model=ApiResponse[GarmentRepairTypeResponse])
async def update_garment_repair_type(
    garment_id: UUID,
    repair_type_id: UUID,
    update_data: GarmentRepairTypeUpdate,
    store_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    garment_repair_type_service = GarmentRepairTypeService(db)
    
    return await garment_repair_type_service.update_garment_repair_type(
        garment_id, 
        repair_type_id, 
        store_id, 
        update_data
    )

@router.put("/{garment_id}/repair-types/activate", response_model=ApiResponse[bool])
async def activate_garment_repair_type(
    garment_id: UUID,
    activate_data: GarmentRepairTypeActivate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    garment_repair_type_service = GarmentRepairTypeService(db)
    
    return await garment_repair_type_service.activate_garment_repair_type(activate_data)

@router.put("/{garment_id}/repair-types/deactivate", response_model=ApiResponse[bool])
async def deactivate_garment_repair_type(
    garment_id: UUID,
    deactivate_data: GarmentRepairTypeDeactivate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    garment_repair_type_service = GarmentRepairTypeService(db)
    
    return await garment_repair_type_service.deactivate_garment_repair_type(deactivate_data)
