from fastapi import APIRouter, Depends
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.schemas.api_response import ApiResponse
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse, RoleActivate, RoleDeactivate
from app.services.role_service import RoleService
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=ApiResponse[RoleResponse])
async def create_role(
    role_data: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    role_service = RoleService(db)
    
    return await role_service.create_role(role_data)

@router.put("/deactivate", response_model=ApiResponse[bool])
async def deactivate_role(
    role_data: RoleDeactivate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    role_service = RoleService(db)
    
    return await role_service.deactivate_role(role_data)

@router.put("/activate", response_model=ApiResponse[bool])
async def activate_role(
    role_data: RoleActivate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    role_service = RoleService(db)
    
    return await role_service.activate_role(role_data)

@router.put("/{role_id}", response_model=ApiResponse[RoleResponse])
async def update_role(
    role_id: UUID,
    role_data: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    role_service = RoleService(db)

    return await role_service.update_role(role_id, role_data)

@router.get("/", response_model=ApiResponse[List[RoleResponse]])
async def get_roles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)) -> ApiResponse[List[RoleResponse]]:
    role_service = RoleService(db)

    return await role_service.get_roles()
