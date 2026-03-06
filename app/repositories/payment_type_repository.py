from sqlalchemy.ext.asyncio import AsyncSession
from app.models.payment_type import PaymentType
from app.repositories.base import BaseRepository

class PaymentTypeRepository(BaseRepository[PaymentType]):
    def __init__(self, db: AsyncSession):
        super().__init__(PaymentType, db)
