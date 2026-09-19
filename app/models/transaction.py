from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.sql import func

from app.database.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    sender_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sender_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    recipient_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)

    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="KES")

    # pending_approval | completed | rejected | failed
    status = Column(String, nullable=False, default="pending_approval")

    # Device the transaction was initiated from (may be untrusted/unknown)
    initiated_device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)

    # Device that approved/rejected it — must be a trusted device
    decision_device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    decided_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)