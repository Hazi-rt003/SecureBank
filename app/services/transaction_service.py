from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.account import Account
from app.models.user import User
from app.schemas.transaction import TransactionCreate
from app.services.account_service import get_account_by_user, get_account_by_number
from app.services.device_service import get_device_by_fingerprint
from app.services.notification_service import (
    notify_transaction_approval_request,
    notify_transaction_decision,
)


def initiate_transaction(
    db: Session,
    user: User,
    payload: TransactionCreate,
    device_fingerprint: str | None,
) -> Transaction:
    sender_account = get_account_by_user(db, user.id)
    if not sender_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sender has no account",
        )

    recipient_account = get_account_by_number(db, payload.recipient_account_number)
    if not recipient_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient account not found",
        )

    if recipient_account.id == sender_account.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot send a transaction to your own account",
        )

    if sender_account.balance < payload.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient funds",
        )

    initiated_device = None
    if device_fingerprint:
        initiated_device = get_device_by_fingerprint(db, user.id, device_fingerprint)

    transaction = Transaction(
        sender_user_id=user.id,
        sender_account_id=sender_account.id,
        recipient_account_id=recipient_account.id,
        amount=payload.amount,
        currency=payload.currency or sender_account.currency,
        status="pending_approval",
        initiated_device_id=initiated_device.id if initiated_device else None,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    notify_transaction_approval_request(
        user_id=user.id,
        transaction_id=transaction.id,
        amount=transaction.amount,
        currency=transaction.currency,
    )

    return transaction


def get_pending_transactions(db: Session, user_id: int) -> list[Transaction]:
    return (
        db.query(Transaction)
        .filter(
            Transaction.sender_user_id == user_id,
            Transaction.status == "pending_approval",
        )
        .order_by(Transaction.created_at.desc())
        .all()
    )


def _get_owned_pending_transaction(db: Session, user_id: int, transaction_id: int) -> Transaction:
    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id,
            Transaction.sender_user_id == user_id,
        )
        .first()
    )
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    if transaction.status != "pending_approval":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transaction is already '{transaction.status}', not pending",
        )
    return transaction


def _require_trusted_device(db: Session, user_id: int, device_fingerprint: str | None):
    if not device_fingerprint:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A device fingerprint is required to approve or reject a transaction",
        )

    device = get_device_by_fingerprint(db, user_id, device_fingerprint)
    if not device or not device.trusted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Transaction approval must come from a trusted device",
        )
    return device


def approve_transaction(
    db: Session, user: User, transaction_id: int, device_fingerprint: str | None
) -> Transaction:
    transaction = _get_owned_pending_transaction(db, user.id, transaction_id)
    device = _require_trusted_device(db, user.id, device_fingerprint)

    sender_account = get_account_by_user(db, user.id)
    # Re-check balance at approval time — it may have changed since initiation.
    if sender_account.balance < transaction.amount:
        transaction.status = "failed"
        transaction.decision_device_id = device.id
        transaction.decided_at = datetime.now(timezone.utc)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient funds at approval time",
        )

    recipient_account = (
        db.query(Account).filter(Account.id == transaction.recipient_account_id).first()
    )

    sender_account.balance -= transaction.amount
    recipient_account.balance += transaction.amount

    transaction.status = "completed"
    transaction.decision_device_id = device.id
    now = datetime.now(timezone.utc)
    transaction.decided_at = now
    transaction.completed_at = now

    db.commit()
    db.refresh(transaction)

    notify_transaction_decision(
        user_id=user.id,
        transaction_id=transaction.id,
        status=transaction.status,
    )

    return transaction


def reject_transaction(
    db: Session, user: User, transaction_id: int, device_fingerprint: str | None
) -> Transaction:
    transaction = _get_owned_pending_transaction(db, user.id, transaction_id)
    device = _require_trusted_device(db, user.id, device_fingerprint)

    transaction.status = "rejected"
    transaction.decision_device_id = device.id
    transaction.decided_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(transaction)

    notify_transaction_decision(
        user_id=user.id,
        transaction_id=transaction.id,
        status=transaction.status,
    )

    return transaction