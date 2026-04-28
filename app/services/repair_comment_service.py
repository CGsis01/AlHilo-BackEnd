from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.repositories.repair_comment_repository import RepairCommentRepository
from app.schemas.api_response import ApiResponse
from app.schemas.repair_comment import RepairCommentCreate, RepairCommentResponse

class RepairCommentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.comment_repository = RepairCommentRepository(db)

    async def add_comment(self, comment_data: RepairCommentCreate) -> ApiResponse[RepairCommentResponse]:
        response = ApiResponse[RepairCommentResponse](
            status=200,
            message="Comment added successfully",
            code="SUCCESS",
            data=None)

        try:
            comment = await self.comment_repository.create_comment(comment_data.model_dump())
            response.data = RepairCommentResponse.model_validate(comment)
        except Exception as e:
            import traceback
            traceback.print_exc()
            await self.db.rollback()
            response.status = 500
            response.message = str(e)
            response.code = "COMMENT_CREATION_ERROR"

        return response

    async def get_comments(self, repair_id: UUID) -> ApiResponse[List[RepairCommentResponse]]:
        response = ApiResponse[List[RepairCommentResponse]](
            status=200,
            message="Comments retrieved successfully",
            code="SUCCESS",
            data=None)

        try:
            comments = await self.comment_repository.get_by_repair(repair_id)
            response.data = [RepairCommentResponse.model_validate(c) for c in comments]
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "COMMENT_RETRIEVAL_ERROR"

        return response
