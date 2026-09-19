from sqlalchemy import Column, DateTime, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class PasskeyCredential(Base):
    __tablename__ = "passkey_credentials"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)

    # base64url-encoded WebAuthn credential ID (must stay unique across all users)
    credential_id = Column(String, unique=True, nullable=False, index=True)

    # COSE-encoded public key bytes, as returned by the authenticator
    public_key = Column(LargeBinary, nullable=False)

    sign_count = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    device = relationship("Device")