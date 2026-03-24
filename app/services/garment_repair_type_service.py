from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.garment_repair_type_repository import GarmentRepairTypeRepository
from app.schemas.api_response import ApiResponse
from app.schemas.garment_repair_type import (
    GarmentRepairTypeCreate,
    GarmentRepairTypeUpdate,
    GarmentRepairTypeActivate,
    GarmentRepairTypeDeactivate,
    GarmentRepairTypeResponse
)

class GarmentRepairTypeService:
    """Service layer for Garment Repair Type relationship operations"""
    def __init__(self, db: AsyncSession):
        self.db = db
        self.garment_repair_type_repository = GarmentRepairTypeRepository(db)

    async def add_repair_type_to_garment(
        self, 
        relationship_data: GarmentRepairTypeCreate
    ) -> ApiResponse[GarmentRepairTypeResponse]:
        response = ApiResponse[GarmentRepairTypeResponse](
            status=201,
            message="Repair type added to garment successfully",
            code="SUCCESS",
            data=None)

        try:
            # Check if relationship already exists
            existing = await self.garment_repair_type_repository.get_by_garment_and_repair_type(
                relationship_data.garment_id,
                relationship_data.repair_type_id,
                relationship_data.store_id)

            if existing:
                response.status = 409
                response.message = "This repair type is already associated with this garment"
                response.code = "RELATIONSHIP_ALREADY_EXISTS"

                return response

            relationship_dict = relationship_data.model_dump()
            garment_repair_type = await self.garment_repair_type_repository.create(relationship_dict)

            # Refresh to load repair_type relationship
            await self.db.refresh(garment_repair_type, ["repair_type"])

            # Build response data with repair type details
            response.data = GarmentRepairTypeResponse(
                repair_type_id=UUID(str(garment_repair_type.repair_type_id)),
                repair_type_name=garment_repair_type.repair_type.name,
                repair_type_code=garment_repair_type.repair_type.code,
                is_default=bool(garment_repair_type.is_default),
                estimated_price_override=float(str(garment_repair_type.estimated_price_override)) if garment_repair_type.estimated_price_override is not None else None,
                estimated_time_override=int(str(garment_repair_type.estimated_time_override)) if garment_repair_type.estimated_time_override is not None else None,
                sort_order=int(str(garment_repair_type.sort_order)) if garment_repair_type.sort_order is not None else None,
                store_id=UUID(str(garment_repair_type.store_id)),
                is_active=bool(garment_repair_type.is_active))
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "GARMENT_REPAIR_TYPE_CREATION_ERROR"

        return response

    async def update_garment_repair_type(
        self,
        garment_id: UUID,
        repair_type_id: UUID,
        store_id: UUID,
        update_data: GarmentRepairTypeUpdate
    ) -> ApiResponse[GarmentRepairTypeResponse]:
        response = ApiResponse[GarmentRepairTypeResponse](
            status=200,
            message="Garment repair type relationship updated successfully",
            code="SUCCESS",
            data=None)
        
        try:
            garment_repair_type = await self.garment_repair_type_repository.get_by_garment_and_repair_type(
                garment_id,
                repair_type_id,
                store_id)

            if not garment_repair_type:
                response.status = 404
                response.message = "Relationship not found"
                response.code = "GARMENT_REPAIR_TYPE_NOT_FOUND"

                return response
            
            update_dict = update_data.model_dump(exclude_unset=True)
            updated_relationship = await self.garment_repair_type_repository.update_relationship(
                garment_id,
                repair_type_id,
                store_id,
                update_dict
            )

            if updated_relationship is None:
                response.status = 404
                response.message = "Relationship not found during update"
                response.code = "GARMENT_REPAIR_TYPE_NOT_FOUND"
                return response

            # Build response with repair type details
            response.data = GarmentRepairTypeResponse(
                repair_type_id=UUID(str(updated_relationship.repair_type_id)),
                repair_type_name=updated_relationship.repair_type.name,
                repair_type_code=updated_relationship.repair_type.code,
                is_default=bool(updated_relationship.is_default),
                estimated_price_override=float(str(updated_relationship.estimated_price_override)) if updated_relationship.estimated_price_override is not None else None,
                estimated_time_override=int(str(updated_relationship.estimated_time_override)) if updated_relationship.estimated_time_override is not None else None,
                sort_order=int(str(updated_relationship.sort_order)) if updated_relationship.sort_order is not None else None,
                is_active=bool(updated_relationship.is_active), 
                store_id=UUID(str(updated_relationship.store_id)))
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "GARMENT_REPAIR_TYPE_UPDATE_ERROR"
        
        return response

    async def deactivate_garment_repair_type(
        self, 
        deactivate_data: GarmentRepairTypeDeactivate
    ) -> ApiResponse[bool]:
        response = ApiResponse[bool](
            status=200,
            message="Garment repair type relationship deactivated successfully",
            code="SUCCESS",
            data=False)

        try:
            result = await self.garment_repair_type_repository.deactivate(
                deactivate_data.garment_id,
                deactivate_data.repair_type_id,
                deactivate_data.store_id,
                deactivate_data.updated_by)

            if not result:
                response.status = 404
                response.message = "Relationship not found"
                response.code = "GARMENT_REPAIR_TYPE_NOT_FOUND"

                return response

            response.data = True
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "GARMENT_REPAIR_TYPE_DEACTIVATION_ERROR"

        return response

    async def activate_garment_repair_type(
        self, 
        activate_data: GarmentRepairTypeActivate
    ) -> ApiResponse[bool]:
        response = ApiResponse[bool](
            status=200,
            message="Garment repair type relationship activated successfully",
            code="SUCCESS",
            data=False)
        
        try:
            result = await self.garment_repair_type_repository.activate(
                activate_data.garment_id,
                activate_data.repair_type_id,
                activate_data.store_id,
                activate_data.updated_by)

            if not result:
                response.status = 404
                response.message = "Relationship not found"
                response.code = "GARMENT_REPAIR_TYPE_NOT_FOUND"

                return response

            response.data = True
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "GARMENT_REPAIR_TYPE_ACTIVATION_ERROR"

        return response

    async def get_garment_repair_types(
        self, 
        garment_id: UUID, 
        store_id: UUID
    ) -> ApiResponse[List[GarmentRepairTypeResponse]]:
        response = ApiResponse[List[GarmentRepairTypeResponse]](
            status=200,
            message="Garment repair types retrieved successfully",
            code="SUCCESS",
            data=[])
        
        try:
            relationships = await self.garment_repair_type_repository.get_by_garment(
                garment_id,
                store_id)

            response.data = [
                GarmentRepairTypeResponse(
                    repair_type_id=UUID(str(rel.repair_type_id)),
                    repair_type_name=rel.repair_type.name,
                    repair_type_code=rel.repair_type.code,
                    is_default=bool(rel.is_default), 
                    estimated_price_override=float(str(rel.estimated_price_override)) if rel.estimated_price_override is not None else None, 
                    estimated_time_override=int(str(rel.estimated_time_override)) if rel.estimated_time_override is not None else None, 
                    sort_order=int(str(rel.sort_order)) if rel.sort_order is not None else None, 
                    store_id=UUID(str(rel.store_id)), 
                    is_active=bool(rel.is_active))
                for rel in relationships]
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "GARMENT_REPAIR_TYPE_RETRIEVAL_ERROR"

        return response
