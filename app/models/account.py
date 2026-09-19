from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.sql import func

from app.database.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    account_number = Column(String, unique=True, nullable=False, index=True)
    balance = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="KES")

    created_at = Column(DateTime(timezone=True), server_default=func.now())