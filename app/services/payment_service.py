from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import aiohttp
from app.core.config import settings
from app.schemas.api_response import ApiResponse
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.repositories.payment_repository import PaymentRepository
from app.repositories.repair_repository import RepairRepository
from app.services.whatsapp_service import WhatsappService

class PaymentService:
    """Service layer for Payment operations"""
    def __init__(self, db: AsyncSession):
        self.db = db
        self.payment_repository = PaymentRepository(db)

    async def create_payment(self, payment_data: PaymentCreate) -> ApiResponse[PaymentResponse]:
        response = ApiResponse[PaymentResponse](
            status=200,
            message="Payment created successfully",
            code="SUCCESS",
            data=None)

        try:
            payment_dict = payment_data.model_dump()

            payment = await self.payment_repository.create(payment_dict)

            response.data = PaymentResponse.model_validate(payment)
        except Exception as e:
            await self.db.rollback()
            response.status = 500
            response.message = str(e)
            response.code = "PAYMENT_CREATION_ERROR"
        
        return response

    async def get_payments(self, filters: Optional[dict] = None) -> ApiResponse[List[PaymentResponse]]:
        response = ApiResponse[List[PaymentResponse]](
            status=200,
            message="Payments retrieved successfully",
            code="SUCCESS",
            data=None)
        
        try:
            payments = await self.payment_repository.get_all_filtered(filters)

            if payments is not None:
                response.data = [PaymentResponse.model_validate(payment) for payment in payments]
            
            return response
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "PAYMENT_RETRIEVAL_ERROR"
        
        return response

    async def save_advance_payment_pdf(self, repair_id: UUID, pdf_bytes: bytes) -> str:
        token = settings.BLOB_READ_WRITE_TOKEN
        filename = f"Alhilo/anticipo/{repair_id}.pdf"
        upload_url = f"https://blob.vercel-storage.com/{filename}"
        async with aiohttp.ClientSession() as session:
            async with session.put(
                upload_url,
                data=pdf_bytes,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/pdf",
                    "access": "public",
                    "x-api-version": "7",
                }
            ) as resp:
                resp.raise_for_status()
                result = await resp.json()
                pdf_url = result["url"]

        repair = await RepairRepository(self.db).get_by_id_with_relations(repair_id)

        if repair:
            whatsapp_service = WhatsappService()
            result = await whatsapp_service.send_advance_payment_pdf(
                phone=repair.customer_phone,
                customer_name=repair.customer_name,
                repair_id=str(repair_id)[:8],
                pdf_url=pdf_url
            )
            print(f"[WhatsApp] Número: {repair.customer_phone}")
            print(f"[WhatsApp] Resultado: {result}")


        return pdf_url
    
    async def save_complete_payment_pdf(self, repair_id: UUID, pdf_bytes: bytes) -> str:
        token = settings.BLOB_READ_WRITE_TOKEN
        filename = f"Alhilo/completo/{repair_id}.pdf"
        upload_url = f"https://blob.vercel-storage.com/{filename}"
        async with aiohttp.ClientSession() as session:
            async with session.put(
                upload_url,
                data=pdf_bytes,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/pdf",
                    "access": "public",
                    "x-api-version": "7",
                }
            ) as resp:
                resp.raise_for_status()
                result = await resp.json()
                pdf_url = result["url"]

        repair = await RepairRepository(self.db).get_by_id_with_relations(repair_id)

        if repair:
            whatsapp_service = WhatsappService()
            result = await whatsapp_service.send_complete_payment_pdf(
                phone=repair.customer_phone,
                customer_name=repair.customer_name,
                repair_id=str(repair_id)[:8],
                pdf_url=pdf_url
            )
            print(f"[WhatsApp] Número: {repair.customer_phone}")
            print(f"[WhatsApp] Resultado: {result}")


        return pdf_url   