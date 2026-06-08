from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, roles, clients, repairs, repair_types, payments, payment_types, repair_status, whatsapp, store, material, repair_complexity, garment, repair_comments, attendance

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(store.router, prefix="/stores", tags=["Stores"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(material.router, prefix="/materials", tags=["Materials"])
api_router.include_router(repair_complexity.router, prefix="/repair-complexities", tags=["RepairComplexities"])
api_router.include_router(repair_types.router, prefix="/repair-types", tags=["RepairTypes"])
api_router.include_router(garment.router, prefix="/garments", tags=["Garments"])
api_router.include_router(clients.router, prefix="/clients", tags=["Clients"])
api_router.include_router(repair_status.router, prefix="/repair-status", tags=["RepairStatus"])
api_router.include_router(repairs.router, prefix="/repairs", tags=["Repairs"])
api_router.include_router(payment_types.router, prefix="/payment-types", tags=["PaymentTypes"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(whatsapp.router, prefix="/whatsapp", tags=["WhatsApp"])
api_router.include_router(repair_comments.router, prefix="/repair-comments", tags=["RepairComments"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["Attendance"])