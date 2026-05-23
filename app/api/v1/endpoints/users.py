from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.database import get_db
from app.schemas.api_response import ApiResponse
from app.schemas.user import UserCreate, UserUpdate, UserActivate, UserDeactivate, UserResponse, UserFilters
from app.services.user_service import UserService
from app.api.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=ApiResponse[List[UserResponse]])
async def get_users(
    role_id: Optional[UUID] = Query(None, description="Filter by role ID"),
    role_code: Optional[str] = Query(None, description="Filter by role code"),
    role_codes: Optional[List[str]] = Query(None, description="Filter by role codes"),
    store_id: Optional[UUID] = Query(None, description="Filter by store ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)) -> ApiResponse[List[UserResponse]]:
    user_service = UserService(db)
    
    filters = UserFilters(
        role_id=role_id,
        role_code=role_code,
        role_codes=role_codes,
        store_id=store_id,
        is_active=is_active,
        search=search
    )
    
    return await user_service.get_users(filters)

@router.get('/unassigned-seamstresses', response_model=ApiResponse[List[UserResponse]])
async def get_unassigned_seamstresses_and_headsewing(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)) -> ApiResponse[List[UserResponse]]:
    user_service = UserService(db)
    
    return await user_service.get_unassigned_seamstresses_and_headsewing()

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)) -> UserResponse:
    
    return UserResponse.model_validate(current_user)

@router.get("/{user_id}", response_model=ApiResponse[UserResponse])
async def get_user(
    user_id: UUID,
    store_id: Optional[UUID] = Query(None, description="Filter materials by store ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)) -> ApiResponse[UserResponse]:
    user_service = UserService(db)
    
    return await user_service.get_user(user_id, store_id)

@router.post("/", response_model=ApiResponse[UserResponse])
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)) -> ApiResponse[UserResponse]:
    user_service = UserService(db)
    
    return await user_service.create_user(user_data)

@router.put("/deactivate", response_model=ApiResponse[bool])
async def deactivate_user(
    user_data: UserDeactivate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    user_service = UserService(db)
    
    return await user_service.deactivate_user(user_data)

@router.put("/activate", response_model=ApiResponse[bool])
async def activate_user(
    user_data: UserActivate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    user_service = UserService(db)
    
    return await user_service.activate_user(user_data)

@router.put("/{user_id}", response_model=ApiResponse[UserResponse])
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)) -> ApiResponse[UserResponse]:
    user_service = UserService(db)
    
    return await user_service.update_user(user_id, user_data)
