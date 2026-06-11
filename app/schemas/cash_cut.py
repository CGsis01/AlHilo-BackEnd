from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class PaymentSummary(BaseModel):
    name: str
    transactions: int
    amount: float

class AdvanceSummary(BaseModel):
    is_advance: bool
    transactions: int
    amount: float

class CashCutMovement(BaseModel):
    payment_id: UUID
    repair_id: UUID
    customer_name: str
    payment_type: str
    amount: float
    is_advance: bool
    voucher_id: str | None
    created_at: datetime

class CardDetail(BaseModel):
    voucher_id: str
    is_debit: bool
    amount: float

class CashCutResponse(BaseModel):
    cash_cut_date: datetime
    cash: PaymentSummary
    card: PaymentSummary
    advances: PaymentSummary
    settlements: PaymentSummary
    total_transactions: int
    grand_total: float
    card_details: list[CardDetail]
    movements: list[CashCutMovement]
