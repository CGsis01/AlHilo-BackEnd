from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.repair_status_repository import RepairStatusRepository
from app.schemas.api_response import ApiResponse
from app.schemas.repair_status import RepairStatusResponse

class RepairStatusService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repair_status_repository = RepairStatusRepository(db)

    async def get_repair_statuses(self) -> ApiResponse[List[RepairStatusResponse]]:
        response = ApiResponse[List[RepairStatusResponse]](
            status=200,
            message="Repair statuses retrieved successfully",
            code="SUCCESS",
            data=None)
        
        try:
            repair_statuses = await self.repair_status_repository.get_all()

            if repair_statuses is not None:
                response.data = [RepairStatusResponse.model_validate(repair_status) for repair_status in repair_statuses]
            
            return response
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_STATUS_RETRIEVAL_ERROR"
        
        return response