from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.garment_repository import GarmentRepository
from app.schemas.api_response import ApiResponse
from app.schemas.garment import (
    GarmentCreate, 
    GarmentUpdate, 
    GarmentActivate, 
    GarmentDeactivate, 
    GarmentResponse
)
from app.schemas.garment_repair_type import GarmentRepairTypeResponse

class GarmentService:
    """Service layer for Garment operations"""
    def __init__(self, db: AsyncSession):
        self.db = db
        self.garment_repository = GarmentRepository(db)

    def _map_garment_to_response(self, garment) -> GarmentResponse:
        """Map garment entity to response schema including repair types"""
        repair_types = [
            GarmentRepairTypeResponse(
                repair_type_id=grt.repair_type_id,
                repair_type_name=grt.repair_type.name,
                repair_type_code=grt.repair_type.code,
                is_default=grt.is_default,
                estimated_price_override=grt.estimated_price_override,
                estimated_time_override=grt.estimated_time_override,
                sort_order=grt.sort_order,
                store_id=garment.store_id,
                is_active=grt.is_active)
            for grt in garment.garment_repair_types]

        return GarmentResponse(
            id=garment.id,
            name=garment.name,
            code=garment.code,
            description=garment.description,
            category=garment.category,
            store_id=garment.store_id,
            is_active=garment.is_active,
            created_at=garment.created_at,
            updated_at=garment.updated_at,
            repair_types=repair_types)

    async def create_garment(self, garment_data: GarmentCreate) -> ApiResponse[GarmentResponse]:
        response = ApiResponse[GarmentResponse](
            status=201,
            message="Garment created successfully",
            code="SUCCESS",
            data=None)
        
        try:
            garment_dict = garment_data.model_dump()
            garment = await self.garment_repository.create(garment_dict)

            # Refresh to load relationships
            await self.db.refresh(garment, ["garment_repair_types"])

            response.data = self._map_garment_to_response(garment)
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "GARMENT_CREATION_ERROR"

        return response

    async def update_garment(self, garment_id: UUID, garment_data: GarmentUpdate) -> ApiResponse[GarmentResponse]:
        response = ApiResponse[GarmentResponse](
            status=200,
            message="Garment updated successfully",
            code="SUCCESS",
            data=None)
        
        try:
            garment = await self.garment_repository.get_by_id_with_relationship(garment_id)
            if not garment:
                response.status = 404
                response.message = "No garment found with the provided ID"
                response.code = "GARMENT_RETRIEVAL_ERROR"

                return response

            update_dict = garment_data.model_dump(exclude_unset=True)

            updated_garment = await self.garment_repository.update(garment_id, update_dict)

            # Refresh to load relationships
            await self.db.refresh(updated_garment, ["garment_repair_types"])

            response.data = self._map_garment_to_response(updated_garment)
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "GARMENT_UPDATE_ERROR"

        return response

    async def deactivate_garment(self, garment_data: GarmentDeactivate) -> ApiResponse[bool]:
        response = ApiResponse[bool](
            status=200,
            message="Garment deactivated successfully",
            code="SUCCESS",
            data=False)

        try:
            garment = await self.garment_repository.get_by_id(garment_data.id)
            if not garment:
                response.status = 404
                response.message = "No garment found with the provided ID"
                response.code = "GARMENT_RETRIEVAL_ERROR"

                return response

            await self.garment_repository.deactivate(garment_data.id, garment_data.updated_by)
            response.data = True
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "GARMENT_DEACTIVATION_ERROR"

        return response

    async def activate_garment(self, garment_data: GarmentActivate) -> ApiResponse[bool]:
        response = ApiResponse[bool](
            status=200,
            message="Garment activated successfully",
            code="SUCCESS",
            data=False)

        try:
            garment = await self.garment_repository.get_by_id(garment_data.id)
            if not garment:
                response.status = 404
                response.message = "No garment found with the provided ID"
                response.code = "GARMENT_RETRIEVAL_ERROR"

                return response

            await self.garment_repository.activate(garment_data.id, garment_data.updated_by)

            response.data = True
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "GARMENT_ACTIVATION_ERROR"

        return response

    async def get_garments(self, store_id: Optional[UUID] = None) -> ApiResponse[List[GarmentResponse]]:
        response = ApiResponse[List[GarmentResponse]](
            status=200,
            message="Garments retrieved successfully",
            code="SUCCESS",
            data=[])

        try:
            if store_id:
                garments = await self.garment_repository.get_by_store(store_id)
            else:
                garments_result = await self.garment_repository.get_all_with_relationship()
                garments = list(garments_result) if garments_result else []
                
            response.data = [self._map_garment_to_response(garment) for garment in garments]
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "GARMENT_RETRIEVAL_ERROR"

        return response

    async def get_garment_by_id(self, garment_id: UUID) -> ApiResponse[GarmentResponse]:
        response = ApiResponse[GarmentResponse](
            status=200,
            message="Garment retrieved successfully",
            code="SUCCESS",
            data=None)

        try:
            garment = await self.garment_repository.get_by_id_with_relationship(garment_id)
            if not garment:
                response.status = 404
                response.message = "No garment found with the provided ID"
                response.code = "GARMENT_RETRIEVAL_ERROR"

                return response

            response.data = self._map_garment_to_response(garment)
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "GARMENT_RETRIEVAL_ERROR"

        return response
