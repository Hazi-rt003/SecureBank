from datetime import datetime

from pydantic import BaseModel


class SessionResponse(BaseModel):
    id: int
    device_id: int | None
    created_at: datetime | None
    expires_at: datetime
    revoked_at: datetime | None
    is_current: bool = False

    class Config:
        from_attributes = True