from datetime import datetime

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: int
    action: str
    details: str | None
    ip_address: str | None
    device_fingerprint: str | None
    created_at: datetime | None

    class Config:
        from_attributes = True