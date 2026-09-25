from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    recipient_account_number: str
    amount: Decimal = Field(gt=0)
    currency: str | None = None


class TransactionResponse(BaseModel):
    id: int
    sender_account_id: int
    recipient_account_id: int
    amount: Decimal
    currency: str
    status: str
    risk_score: int
    risk_level: str

    created_at: datetime | None
    decided_at: datetime | None
    completed_at: datetime | None

    class Config:
        from_attributes = True