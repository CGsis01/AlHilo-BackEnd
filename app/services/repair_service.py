from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.models.repair_item import RepairItem
from app.repositories.repair_repository import RepairRepository
from app.schemas.api_response import ApiResponse
from app.schemas.repair import AssignRepair, RepairCreate, RepairUpdate, RepairResponse, UpdateStatus
from fastapi import HTTPException, status

class RepairService:
    """Service layer for Repair operations"""
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repair_repository = RepairRepository(db)

    async def create_repair(self, repair_data: RepairCreate) -> ApiResponse[RepairResponse]:
        response = ApiResponse[RepairResponse](
            status=200,
            message="Repair created successfully",
            code="SUCCESS",
            data=None)

        try:
            repair_dict = repair_data.model_dump()
            repair_items = repair_dict.pop("repair_items", [])

            repair = await self.repair_repository.create(repair_dict)

            if repair_items:
                for repair_item in repair_items:
                    item_data = dict(repair_item)
                    item_data["repair_id"] = repair.id
                    item_data["created_by"] = item_data.get("created_by") or repair.created_by
                    self.db.add(RepairItem(**item_data))

                await self.db.commit()
                await self.db.refresh(repair)
                
                repair = await self.repair_repository.get_by_id_with_relations(UUID(str(repair.id)))

            response.data = RepairResponse.model_validate(repair)
        except Exception as e:
            await self.db.rollback()
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_CREATION_ERROR"
        
        return response

    async def update_repair(self, repair_id: UUID, repair_data: RepairUpdate) -> ApiResponse[RepairResponse]:
        response = ApiResponse[RepairResponse](
            status=200,
            message="Repair updated successfully",
            code="SUCCESS",
            data=None)
        
        try:
            repair = await self.repair_repository.get_by_id_with_relations(repair_id)
            if not repair:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Repair not found")
             
            update_dict = repair_data.model_dump(exclude_unset=True)
            repair_items = update_dict.pop("repair_items", None)

            for field, value in update_dict.items():
                setattr(repair, field, value)

            if repair_items:
                existing_items = {item.id: item for item in repair.repair_items}

                for repair_item in repair_items:
                    item_data = dict(repair_item)
                    repair_item_id = item_data.pop("repair_item_id", None)
                    item_data["repair_id"] = repair.id

                    if repair_item_id and repair_item_id in existing_items:
                        db_item = existing_items[repair_item_id]
                        for field, value in item_data.items():
                            if value is not None and field != "repair_id":
                                setattr(db_item, field, value)
                        db_item.updated_by = update_dict.get("updated_by")
                        continue

                    item_data["created_by"] = item_data.get("created_by") or update_dict.get("updated_by")
                    self.db.add(RepairItem(**item_data))
             
            await self.db.commit()
            repair = await self.repair_repository.get_by_id_with_relations(repair_id)
             
            response.data = RepairResponse.model_validate(repair)
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            await self.db.rollback()
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_UPDATE_ERROR"
        
        return response

    async def assign_repair(self, repair_id: UUID, assign_repair_data: AssignRepair) -> ApiResponse[RepairResponse]:
        response = ApiResponse[RepairResponse](
            status=200,
            message="Repair assigned successfully",
            code="SUCCESS",
            data=None)

        try:
            repair = await self.repair_repository.get_by_id_with_relations(repair_id)
            if not repair:
                response.status = status.HTTP_404_NOT_FOUND
                response.message = "Repair not found"
                response.code = "REPAIR_NOT_FOUND"
                
                return response
            
            update_dict = assign_repair_data.model_dump(exclude_unset=True, exclude={'repair_id'})

            assigned_repair = await self.repair_repository.update(repair_id, update_dict)

            response.data = RepairResponse.model_validate(assigned_repair)
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_ASSIGNMENT_ERROR"
        
        return response

    async def update_repair_status(self, repair_id: UUID, update_status_data: UpdateStatus) -> ApiResponse[RepairResponse]:
        response = ApiResponse[RepairResponse](
            status=200,
            message="Repair status updated successfully",
            code="SUCCESS",
            data=None)

        try:
            repair = await self.repair_repository.get_by_id_with_relations(repair_id)
            if not repair:
                response.status = status.HTTP_404_NOT_FOUND
                response.message = "Repair not found"
                response.code = "REPAIR_NOT_FOUND"
                
                return response
            
            update_dict = update_status_data.model_dump(exclude_unset=True, exclude={'repair_id'})

            updated_repair = await self.repair_repository.update(repair_id, update_dict)

            response.data = RepairResponse.model_validate(updated_repair)
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_STATUS_UPDATE_ERROR"
        
        return response

    async def get_repairs(self, filters: Optional[dict] = None) -> ApiResponse[List[RepairResponse]]:
        response = ApiResponse[List[RepairResponse]](
            status=200,
            message="Repairs retrieved successfully",
            code="SUCCESS",
            data=None)
        
        try:
            repairs = await self.repair_repository.get_all_filtered(filters)

            if repairs is not None:
                response.data = [RepairResponse.model_validate(repair) for repair in repairs]
            
            return response
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_RETRIEVAL_ERROR"
        
        return response

    async def get_repair(self, repair_id: UUID) -> ApiResponse[RepairResponse]:
        response = ApiResponse[RepairResponse](
            status=200,
            message="Repair retrieved successfully",
            code="SUCCESS",
            data=None)
        
        try:
             repair = await self.repair_repository.get_by_id_with_relations(repair_id)
             if not repair:
                 raise HTTPException(
                     status_code=status.HTTP_404_NOT_FOUND,
                     detail="Repair not found")
             
             response.data = RepairResponse.model_validate(repair)
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_RETRIEVAL_ERROR"
        
        return response

    async def get_repairs_by_client(self, client_id: UUID) -> ApiResponse[List[RepairResponse]]:
        response = ApiResponse[List[RepairResponse]](
            status=200,
            message="Repairs retrieved successfully",
            code="SUCCESS",
            data=None)
        
        try:
            repairs = await self.repair_repository.get_by_client(client_id)
            response.data = [RepairResponse.model_validate(repair) for repair in repairs]
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_RETRIEVAL_ERROR"
        
        return response

    async def get_repairs_by_status(self, status_id: UUID) -> ApiResponse[List[RepairResponse]]:
        response = ApiResponse[List[RepairResponse]](
            status=200,
            message="Repairs retrieved successfully",
            code="SUCCESS",
            data=None)
        
        try:
            repairs = await self.repair_repository.get_by_status(status_id)
            response.data = [RepairResponse.model_validate(repair) for repair in repairs]
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_RETRIEVAL_ERROR"
        
        return response

    async def get_estimated_time_repairs(self) -> ApiResponse[int]:
        response = ApiResponse[int](
            status=200,
            message="Repairs retrieved successfully",
            code="SUCCESS",
            data=None)
        
        try:
            repairs_estimated_time = await self.repair_repository.get_estimated_time()
            
            response.data = repairs_estimated_time
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_RETRIEVAL_ERROR"
        
        return response