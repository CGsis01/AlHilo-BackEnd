from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.repair_type_repository import RepairTypeRepository
from app.schemas.api_response import ApiResponse
from app.schemas.repair_type import RepairTypeCreate, RepairTypeUpdate, RepairTypeActivate, RepairTypeDeactivate, RepairTypeResponse

class RepairTypeService:
    """Service layer for RepairType operations"""
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repair_type_repository = RepairTypeRepository(db)

    async def create_repair_type(self, repair_type_data: RepairTypeCreate) -> ApiResponse[RepairTypeResponse]:
        response = ApiResponse[RepairTypeResponse](
            status=201,
            message="Repair type created successfully",
            code="SUCCESS",
            data=None)
        
        try:
            repair_type_dict = repair_type_data.model_dump()
            repair_type = await self.repair_type_repository.create(repair_type_dict)

            response.data = RepairTypeResponse.model_validate(repair_type)
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_TYPE_CREATION_ERROR"

        return response

    async def update_repair_type(self, repair_type_id: UUID, repair_type_data: RepairTypeUpdate) -> ApiResponse[RepairTypeResponse]:
        response = ApiResponse[RepairTypeResponse](
            status=200,
            message="Repair type updated successfully",
            code="SUCCESS",
            data=None)
        
        try:
            repair_type = await self.repair_type_repository.get_by_id(repair_type_id)
            if not repair_type:
                response.status = 404
                response.message = "No repair type found with the provided ID"
                response.code = "REPAIR_TYPE_RETRIEVAL_ERROR"

                return response

            update_dict = repair_type_data.model_dump(exclude_unset=True)

            updated_repair_type = await self.repair_type_repository.update(repair_type_id, update_dict)

            response.data = RepairTypeResponse.model_validate(updated_repair_type)
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_TYPE_UPDATE_ERROR"
        
        return response

    async def deactivate_repair_type(self, repair_type_data: RepairTypeDeactivate) -> ApiResponse[bool]:
        response = ApiResponse[bool](
            status=200,
            message="Repair type deactivated successfully",
            code="SUCCESS",
            data=False)
        
        try:
            repair_type = await self.repair_type_repository.get_by_id(repair_type_data.id)
            if not repair_type:
                response.status = 404
                response.message = "No repair type found with the provided ID"
                response.code = "REPAIR_TYPE_RETRIEVAL_ERROR"

                return response
            
            await self.repair_type_repository.deactivate_repair_type(repair_type_data.id, repair_type_data.updated_by)
            
            response.data = True
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_TYPE_DEACTIVATE_ERROR"
        
        return response

    async def activate_repair_type(self, repair_type_data: RepairTypeActivate) -> ApiResponse[bool]:
        response = ApiResponse[bool](
            status=200,
            message="Repair type activated successfully",
            code="SUCCESS",
            data=False)
        
        try:
            repair_type = await self.repair_type_repository.get_by_id(repair_type_data.id)
            if not repair_type:
                response.status = 404
                response.message = "No repair type found with the provided ID"
                response.code = "REPAIR_TYPE_RETRIEVAL_ERROR"

                return response

            await self.repair_type_repository.activate_repair_type(repair_type_data.id, repair_type_data.updated_by)

            response.data = True
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_TYPE_ACTIVATE_ERROR"
        
        return response

    async def get_repair_types(self) -> ApiResponse[List[RepairTypeResponse]]:
        response = ApiResponse[List[RepairTypeResponse]](
            status=200,
            message="Repair types retrieved successfully",
            code="SUCCESS",
            data=None)
        
        try:
            repair_types = await self.repair_type_repository.get_all()

            if repair_types is not None:
                response.data = [RepairTypeResponse.model_validate(repair_type) for repair_type in repair_types]
            
            return response
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_TYPE_RETRIEVAL_ERROR"
        
        return response
