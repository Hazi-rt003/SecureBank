from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.database.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Nullable: a failed login with a bogus email has no real user to attach to.
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    action = Column(String, nullable=False, index=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)
    device_fingerprint = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())