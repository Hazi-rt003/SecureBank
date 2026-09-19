from decimal import Decimal

from pydantic import BaseModel


class AccountResponse(BaseModel):
    id: int
    account_number: str
    balance: Decimal
    currency: str

    class Config:
        from_attributes = True