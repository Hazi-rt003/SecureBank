from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    device_name = Column(
        String,
        nullable=False,
    )

    device_id = Column(
        String, 
        unique=True, 
        nullable=False,
        )
    
    device_type = Column(String)

    device_fingerprint = Column(
        String,
        unique=True,
        nullable=False,
    )

    platform = Column(
        String,
        nullable=False,
    )

    trusted = Column(
        Boolean,
        default=False,
    )

    last_seen = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship(
        "User",
        back_populates="devices"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )