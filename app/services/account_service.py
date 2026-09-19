import os
import random
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.account import Account

# NOTE: demo-only convenience so you can test transactions without a real
# deposit/funding flow. Replace with actual funding logic before this is
# anything more than a local dev project.
STARTING_BALANCE = Decimal(os.getenv("STARTING_ACCOUNT_BALANCE", "1000.00"))
DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "KES")


def _generate_account_number() -> str:
    return "SB" + "".join(str(random.randint(0, 9)) for _ in range(10))


def create_account_for_user(db: Session, user_id: int) -> Account:
    for _ in range(5):
        account_number = _generate_account_number()
        if not db.query(Account).filter(Account.account_number == account_number).first():
            break
    else:
        raise RuntimeError("Could not generate a unique account number")

    account = Account(
        user_id=user_id,
        account_number=account_number,
        balance=STARTING_BALANCE,
        currency=DEFAULT_CURRENCY,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def get_account_by_user(db: Session, user_id: int) -> Account | None:
    return db.query(Account).filter(Account.user_id == user_id).first()


def get_account_by_number(db: Session, account_number: str) -> Account | None:
    return db.query(Account).filter(Account.account_number == account_number).first()