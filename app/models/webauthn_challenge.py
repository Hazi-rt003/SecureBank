from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.database.database import Base


class WebAuthnChallenge(Base):
    __tablename__ = "webauthn_challenges"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)

    challenge = Column(String, nullable=False)  # base64url-encoded

    # "registration" for now; "authentication" is the hook for future login step-up
    purpose = Column(String, nullable=False, default="registration")

    created_at = Column(DateTime(timezone=True), server_default=func.now())