from pydantic import BaseModel


class DeviceCreate(BaseModel):
    device_name: str
    device_id: str
    device_type: str | None = None
    device_fingerprint: str
    platform: str


class DeviceResponse(BaseModel):
    id: int
    user_id: int
    device_name: str
    device_id: str
    device_type: str | None
    device_fingerprint: str
    platform: str
    trusted: bool
    last_seen: object | None
    created_at: object | None

    class Config:
        from_attributes = True