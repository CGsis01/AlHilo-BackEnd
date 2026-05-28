from typing import Any, Dict, List, Optional, cast
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.models.repair_item import RepairItem
from app.models.repair_item_repair_type import RepairItemRepairType
from app.models.repair_status import RepairStatus
from app.repositories.repair_repository import RepairRepository
from app.repositories.repair_item_repository import RepairItemRepository
from app.schemas.api_response import ApiResponse
from app.schemas.repair import AssignRepairGarments, AssignRepairItem, RepairCreate, RepairUpdate, RepairResponse, UpdateRepairItemStatus, UpdateStatus
from app.schemas.repair_item import RepairItemResponse
from app.services.repair_realtime_service import repair_realtime_broker
from fastapi import HTTPException, status

class RepairService:
    """Service layer for Repair operations"""
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repair_repository = RepairRepository(db)
        self.repair_item_repository = RepairItemRepository(db)

    def _get_aggregate_status_name(self, repair) -> str:
        item_status_names = {
            item.repair_status.name
            for item in (repair.repair_items or [])
            if item.repair_status is not None and item.repair_status.name
        }
        
        if not item_status_names:
            return repair.repair_status.name if repair.repair_status and repair.repair_status.name else "Pendiente"

        # Priority rules for aggregate status:
        # 1) All delivered -> delivered
        # 2) All validated -> validated
        # 3) All pending -> pending
        # 4) Any non-pending item -> in progress
        if item_status_names == {"Entregada"}:
            return "Entregada"
        if item_status_names == {"Validada"}:
            return "Validada"
        if item_status_names == {"Pendiente"}:
            return "Pendiente"
        if any(status_name != "Pendiente" for status_name in item_status_names):
            return "En progreso"

        return "Pendiente"

    def _is_in_date_range(self, value: Optional[datetime], date_from: Optional[datetime], date_to: Optional[datetime]) -> bool:
        if value is None:
            return True

        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            value = value.replace(tzinfo=timezone.utc)

        if date_from is not None:
            from_value = date_from
            if from_value.tzinfo is None or from_value.tzinfo.utcoffset(from_value) is None:
                from_value = from_value.replace(tzinfo=timezone.utc)
            if value < from_value:
                return False

        if date_to is not None:
            to_value = date_to
            if to_value.tzinfo is None or to_value.tzinfo.utcoffset(to_value) is None:
                to_value = to_value.replace(tzinfo=timezone.utc)
            if value > to_value:
                return False

        return True

    async def _sync_repair_status_from_items(self, repair_id: UUID) -> Optional[RepairResponse]:
        repair = await self.repair_repository.get_by_id_with_relations(repair_id)
        if not repair:
            return None

        target_status_name = self._get_aggregate_status_name(repair)

        current_status_name = repair.repair_status.name if repair.repair_status else None
        if current_status_name != target_status_name:
            status_result = await self.db.execute(
                select(RepairStatus).filter(RepairStatus.name == target_status_name))

            status = status_result.scalar_one_or_none()
            if status:
                await self.repair_repository.update(UUID(str(repair.id)), {"repair_status_id": status.repair_status_id})
                repair = await self.repair_repository.get_by_id_with_relations(repair_id)

        return RepairResponse.model_validate(repair)

    async def _emit_repair_realtime_event(
        self,
        event_type: str,
        repair: Optional[RepairResponse],
        updated_by: Optional[UUID] = None,
        repair_item_id: Optional[UUID] = None,
        status_id: Optional[UUID] = None,
    ) -> None:
        if repair is None:
            return

        payload = {
            "event": event_type,
            "repair_id": str(repair.id),
            "repair_item_id": str(repair_item_id) if repair_item_id else None,
            "status_id": str(status_id) if status_id else None,
            "updated_by": str(updated_by) if updated_by else None,
            "updated_at": datetime.utcnow().isoformat() + "Z",
            # Full snapshot included for Phase 2 UI patching without extra HTTP calls.
            "repair": repair.model_dump(mode="json"),
        }

        await repair_realtime_broker.broadcast(payload)

    async def get_repair_stats(self, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None) -> ApiResponse[Dict[str, Any]]:
        response = ApiResponse[Dict[str, Any]](
            status=200,
            message="Repair stats retrieved successfully",
            code="SUCCESS",
            data=None)

        try:
            repairs = await self.repair_repository.get_all_filtered()

            filtered_repairs = [
                repair for repair in repairs
                if self._is_in_date_range(cast(datetime, repair.received_date), date_from, date_to)
            ]

            status_counts = {
                "Pendiente": 0,
                "En progreso": 0,
                "Por Validar": 0,
                "Validada": 0,
                "Entregada": 0,
            }

            for repair in filtered_repairs:
                aggregate_status = self._get_aggregate_status_name(repair)
                if aggregate_status in status_counts:
                    status_counts[aggregate_status] += 1

            response.data = {
                "total": len(filtered_repairs),
                "pending": status_counts["Pendiente"],
                "in_progress": status_counts["En progreso"],
                "in_validation": status_counts["Por Validar"],
                "validated": status_counts["Validada"],
                "completed": status_counts["Validada"],
                "delivered": status_counts["Entregada"],
                "cancelled": 0,
            }
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_STATS_RETRIEVAL_ERROR"

        return response

    async def get_repair_reports_summary(self, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None) -> ApiResponse[Dict[str, Any]]:
        response = ApiResponse[Dict[str, Any]](
            status=200,
            message="Repair reports summary retrieved successfully",
            code="SUCCESS",
            data=None)

        try:
            repairs = await self.repair_repository.get_all_filtered()

            filtered_repairs = [
                repair for repair in repairs
                if self._is_in_date_range(cast(datetime, repair.received_date), date_from, date_to)
            ]

            status_counts = {
                "Pendiente": 0,
                "En progreso": 0,
                "Por Validar": 0,
                "Validada": 0,
                "Entregada": 0,
            }

            delivered_revenue = 0.0
            for repair in filtered_repairs:
                aggregate_status = self._get_aggregate_status_name(repair)
                if aggregate_status in status_counts:
                    status_counts[aggregate_status] += 1

                if aggregate_status == "Entregada":
                    delivered_revenue += float(cast(float,repair.final_price) or cast(float,repair.estimated_price) or 0)

            response.data = {
                "total_repairs": len(filtered_repairs),
                "total_revenue_delivered": delivered_revenue,
                "status_counts": {
                    "pending": status_counts["Pendiente"],
                    "in_progress": status_counts["En progreso"],
                    "in_validation": status_counts["Por Validar"],
                    "validated": status_counts["Validada"],
                    "delivered": status_counts["Entregada"],
                },
                "date_from": date_from.isoformat() if date_from else None,
                "date_to": date_to.isoformat() if date_to else None,
            }
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_REPORTS_RETRIEVAL_ERROR"

        return response

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
                    repair_types_data = item_data.pop("repair_types", [])
                    item_data["repair_id"] = repair.id
                    item_data["repair_status_id"] = item_data.get("repair_status_id") or repair.repair_status_id
                    item_data["created_by"] = item_data.get("created_by") or repair.created_by
                    new_item = RepairItem(**item_data)
                    self.db.add(new_item)
                    await self.db.flush()

                    for i, rt in enumerate(repair_types_data):
                        self.db.add(RepairItemRepairType(
                            repair_item_id=new_item.id,
                            repair_type_id=rt["repair_type_id"],
                            price=rt["price"],
                            sort_order=i,
                            created_by=repair.created_by
                        ))

                await self.db.commit()
                await self.db.refresh(repair)
                
                repair = await self.repair_repository.get_by_id_with_relations(UUID(str(repair.id)))

            response.data = RepairResponse.model_validate(repair)
            await self._emit_repair_realtime_event(
                event_type="repair.created",
                repair=response.data,
                updated_by=repair_data.created_by,
            )
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
                    repair_types_data = item_data.pop("repair_types", [])
                    item_data["repair_id"] = repair.id

                    if repair_item_id and repair_item_id in existing_items:
                        db_item = existing_items[repair_item_id]
                        for field, value in item_data.items():
                            if value is not None and field != "repair_id":
                                setattr(db_item, field, value)
                        db_item.updated_by = update_dict.get("updated_by")
                        if repair_types_data:
                            await self.db.flush()
                            for rt_row in list(db_item.repair_item_repair_types):
                                await self.db.delete(rt_row)
                            await self.db.flush()
                            for i, rt in enumerate(repair_types_data):
                                self.db.add(RepairItemRepairType(
                                    repair_item_id=db_item.id,
                                    repair_type_id=rt["repair_type_id"],
                                    price=rt["price"],
                                    sort_order=i,
                                    updated_by=update_dict.get("updated_by")
                                ))
                        continue

                    item_data["created_by"] = item_data.get("created_by") or update_dict.get("updated_by")
                    item_data["repair_status_id"] = item_data.get("repair_status_id") or repair.repair_status_id
                    new_item = RepairItem(**item_data)
                    self.db.add(new_item)
                    await self.db.flush()
                    for i, rt in enumerate(repair_types_data):
                        self.db.add(RepairItemRepairType(
                            repair_item_id=new_item.id,
                            repair_type_id=rt["repair_type_id"],
                            price=rt["price"],
                            sort_order=i,
                            created_by=update_dict.get("updated_by")
                        ))
             
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

    async def assign_repair_items(self, repair_id: UUID, assign_garments_data: AssignRepairGarments) -> ApiResponse[RepairResponse]:
        response = ApiResponse[RepairResponse](
            status=200,
            message="Repair items assigned successfully",
            code="SUCCESS",
            data=None)

        try:
            repair = await self.repair_repository.get_by_id_with_relations(repair_id)
            if not repair:
                response.status = status.HTTP_404_NOT_FOUND
                response.message = "Repair not found"
                response.code = "REPAIR_NOT_FOUND"
                
                return response
            
            # Create a dictionary of repair_item_id -> assigned_to_id for bulk assignment
            assignments = {}
            for assignment in assign_garments_data.assignments:
                assignments[assignment.repair_item_id] = assignment.assigned_to_id
                assignments[assignment.repair_item_id] = assignment.attended_by_id  
            
            # Perform bulk assignment
            await self.repair_item_repository.assign_bulk(assignments)
            
            synced_repair = await self._sync_repair_status_from_items(repair_id)
            if not synced_repair:
                response.status = status.HTTP_404_NOT_FOUND
                response.message = "Repair not found"
                response.code = "REPAIR_NOT_FOUND"
                return response

            response.data = synced_repair
            await self._emit_repair_realtime_event(
                event_type="repair.assignment_changed",
                repair=synced_repair,
                updated_by=assign_garments_data.updated_by,
            )
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_ITEM_ASSIGNMENT_ERROR"
        
        return response

    async def assign_single_repair_item(self, repair_item_id: UUID, assignment_data: AssignRepairItem) -> ApiResponse[RepairItemResponse]:
        response = ApiResponse[RepairItemResponse](
            status=200,
            message="Repair item assigned successfully",
            code="SUCCESS",
            data=None)

        try:
            item = await self.repair_item_repository.assign(repair_item_id, assignment_data.assigned_to_id)
            if not item:
                response.status = status.HTTP_404_NOT_FOUND
                response.message = "Repair item not found"
                response.code = "REPAIR_ITEM_NOT_FOUND"
                
                return response

            synced_repair = await self._sync_repair_status_from_items(UUID(str(item.repair_id)))
            if synced_repair:
                await self._emit_repair_realtime_event(
                    event_type="repair.assignment_changed",
                    repair=synced_repair,
                    updated_by=assignment_data.updated_by,
                    repair_item_id=repair_item_id,
                )

            response.data = RepairItemResponse.model_validate(item)
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_ITEM_ASSIGNMENT_ERROR"
        
        return response

    async def get_repair_items_by_seamstress(self, seamstress_id: UUID) -> ApiResponse[List[RepairItemResponse]]:
        response = ApiResponse[List[RepairItemResponse]](
            status=200,
            message="Repair items retrieved successfully",
            code="SUCCESS",
            data=None)
        
        try:
            items = await self.repair_item_repository.get_by_assigned_to(seamstress_id)
            response.data = [RepairItemResponse.model_validate(item) for item in items]
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_ITEM_RETRIEVAL_ERROR"
        
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

            if(updated_repair and updated_repair.repair_items):
                for item in updated_repair.repair_items:
                    item.repair_status_id = update_status_data.repair_status_id

            await self.db.commit()
            updated_repair = await self.repair_repository.get_by_id_with_relations(repair_id)

            response.data = RepairResponse.model_validate(updated_repair)
            await self._emit_repair_realtime_event(
                event_type="repair.status_changed",
                repair=response.data,
                updated_by=update_status_data.updated_by,
                status_id=update_status_data.repair_status_id,
            )
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_STATUS_UPDATE_ERROR"
        
        return response

    async def update_repair_item_status(self, repair_item_id: UUID, item_status_data: UpdateRepairItemStatus) -> ApiResponse[RepairResponse]:
        response = ApiResponse[RepairResponse](
            status=200,
            message="Repair item status updated successfully",
            code="SUCCESS",
            data=None)

        try:
            item = await self.repair_item_repository.update_status(repair_item_id, item_status_data.repair_status_id)
            
            if not item:
                response.status = status.HTTP_404_NOT_FOUND
                response.message = "Repair item not found"
                response.code = "REPAIR_ITEM_NOT_FOUND"
                
                return response

            synced_repair = await self._sync_repair_status_from_items(UUID(str(item.repair_id)))
            if not synced_repair:
                response.status = status.HTTP_404_NOT_FOUND
                response.message = "Repair not found"
                response.code = "REPAIR_NOT_FOUND"
                return response

            response.data = synced_repair
            await self._emit_repair_realtime_event(
                event_type="repair.item_status_changed",
                repair=synced_repair,
                updated_by=item_status_data.updated_by,
                repair_item_id=repair_item_id,
                status_id=item_status_data.repair_status_id,
            )
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_ITEM_STATUS_UPDATE_ERROR"

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
            status_result = await self.db.execute(
                select(RepairStatus).filter(RepairStatus.repair_status_id == status_id)
            )
            target_status = status_result.scalar_one_or_none()

            if not target_status:
                response.data = []
                return response

            repairs = await self.repair_repository.get_all_filtered()
            matching_repairs = [
                repair for repair in repairs
                if self._get_aggregate_status_name(repair) == target_status.name
            ]

            response.data = [RepairResponse.model_validate(repair) for repair in matching_repairs]
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