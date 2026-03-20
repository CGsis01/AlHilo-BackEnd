from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.repair_complexity_repository import RepairComplexityRepository
from app.schemas.api_response import ApiResponse
from app.schemas.repair_complexity import (
    RepairComplexityCreate, 
    RepairComplexityUpdate, 
    RepairComplexityActivate, 
    RepairComplexityDeactivate, 
    RepairComplexityResponse
)

class RepairComplexityService:
    """Service layer for Repair Complexity operations"""
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repair_complexity_repository = RepairComplexityRepository(db)
    
    async def create_repair_complexity(self, repair_complexity_data: RepairComplexityCreate) -> ApiResponse[RepairComplexityResponse]:
        response = ApiResponse[RepairComplexityResponse](
            status=201,
            message="Repair complexity created successfully",
            code="SUCCESS",
            data=None)
        
        try:
            repair_complexity_dict = repair_complexity_data.model_dump()
            repair_complexity = await self.repair_complexity_repository.create(repair_complexity_dict)

            response.data = RepairComplexityResponse.model_validate(repair_complexity)
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_COMPLEXITY_CREATION_ERROR"

        return response

    async def update_repair_complexity(self, repair_complexity_id: UUID, repair_complexity_data: RepairComplexityUpdate) -> ApiResponse[RepairComplexityResponse]:
        response = ApiResponse[RepairComplexityResponse](
            status=200,
            message="Repair complexity updated successfully",
            code="SUCCESS",
            data=None)
        
        try:
            repair_complexity = await self.repair_complexity_repository.get_by_id(repair_complexity_id)
            if not repair_complexity:
                response.status = 404
                response.message = "No repair complexity found with the provided ID"
                response.code = "REPAIR_COMPLEXITY_RETRIEVAL_ERROR"

                return response
            
            update_dict = repair_complexity_data.model_dump(exclude_unset=True)

            updated_repair_complexity = await self.repair_complexity_repository.update(repair_complexity_id, update_dict)
            
            response.data = RepairComplexityResponse.model_validate(updated_repair_complexity)
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_COMPLEXITY_UPDATE_ERROR"
        
        return response

    async def deactivate_repair_complexity(self, repair_complexity_data: RepairComplexityDeactivate) -> ApiResponse[bool]:
        response = ApiResponse[bool](
            status=200,
            message="Repair complexity deactivated successfully",
            code="SUCCESS",
            data=False)
        
        try:
            repair_complexity = await self.repair_complexity_repository.get_by_id(repair_complexity_data.id)
            if not repair_complexity:
                response.status = 404
                response.message = "No repair complexity found with the provided ID"
                response.code = "REPAIR_COMPLEXITY_RETRIEVAL_ERROR"

                return response
            
            await self.repair_complexity_repository.deactivate_repair_complexity(repair_complexity_data.id, repair_complexity_data.updated_by)
            
            response.data = True
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_COMPLEXITY_DEACTIVATION_ERROR"
        
        return response

    async def activate_repair_complexity(self, repair_complexity_data: RepairComplexityActivate) -> ApiResponse[bool]:
        response = ApiResponse[bool](
            status=200,
            message="Repair complexity activated successfully",
            code="SUCCESS",
            data=False)
        
        try:
            repair_complexity = await self.repair_complexity_repository.get_by_id(repair_complexity_data.id)
            if not repair_complexity:
                response.status = 404
                response.message = "No repair complexity found with the provided ID"
                response.code = "REPAIR_COMPLEXITY_RETRIEVAL_ERROR"

                return response
            
            await self.repair_complexity_repository.activate_repair_complexity(repair_complexity_data.id, repair_complexity_data.updated_by)
            
            response.data = True
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_COMPLEXITY_ACTIVATION_ERROR"
        
        return response

    async def get_repair_complexities(self, store_id: Optional[UUID] = None) -> ApiResponse[List[RepairComplexityResponse]]:
        response = ApiResponse[List[RepairComplexityResponse]](
            status=200,
            message="Repair complexities retrieved successfully",
            code="SUCCESS",
            data=[])
        
        try:
            if store_id:
                repair_complexities = await self.repair_complexity_repository.get_by_store(store_id)
            else:
                repair_complexities = await self.repair_complexity_repository.get_all()
            
            response.data = [RepairComplexityResponse.model_validate(rc) for rc in (repair_complexities or [])]
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_COMPLEXITY_RETRIEVAL_ERROR"
        
        return response

    async def get_repair_complexity_by_id(self, repair_complexity_id: UUID) -> ApiResponse[RepairComplexityResponse]:
        response = ApiResponse[RepairComplexityResponse](
            status=200,
            message="Repair complexity retrieved successfully",
            code="SUCCESS",
            data=None)
        
        try:
            repair_complexity = await self.repair_complexity_repository.get_by_id(repair_complexity_id)
            if not repair_complexity:
                response.status = 404
                response.message = "No repair complexity found with the provided ID"
                response.code = "REPAIR_COMPLEXITY_NOT_FOUND"

                return response
            
            response.data = RepairComplexityResponse.model_validate(repair_complexity)
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_COMPLEXITY_RETRIEVAL_ERROR"
        
        return response
