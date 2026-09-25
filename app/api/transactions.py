from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from app.core.limiter import limiter
from app.database.database import get_db
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.security.dependencies import get_current_user
from app.services.transaction_service import (
    initiate_transaction,
    get_pending_transactions,
    approve_transaction,
    reject_transaction,
)

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/", response_model=TransactionResponse)
@limiter.limit("20/minute")
def create_transaction(
    request: Request,
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    device_fingerprint: str | None = Header(default=None, alias="X-Device-Fingerprint"),
):
    return initiate_transaction(db, current_user, payload, device_fingerprint)


@router.get("/pending", response_model=list[TransactionResponse])
def list_pending_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_pending_transactions(db, current_user.id)


@router.post("/{transaction_id}/approve", response_model=TransactionResponse)
@limiter.limit("10/minute")
def approve(
    request: Request,
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    device_fingerprint: str | None = Header(default=None, alias="X-Device-Fingerprint"),
):
    return approve_transaction(db, current_user, transaction_id, device_fingerprint)


@router.post("/{transaction_id}/reject", response_model=TransactionResponse)
@limiter.limit("10/minute")
def reject(
    request: Request,
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    device_fingerprint: str | None = Header(default=None, alias="X-Device-Fingerprint"),
):
    return reject_transaction(db, current_user, transaction_id, device_fingerprint)