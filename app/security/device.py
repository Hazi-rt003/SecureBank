from pydantic import BaseModel


class DeviceCreate(BaseModel):
    device_name: str
    device_id: str
    device_type: str
    device_fingerprint: str
    platform: str


class DeviceResponse(BaseModel):
    id: int
    device_name: str
    device_id: str
    device_type: str
    device_fingerprint: str
    platform: str
    trusted: bool

    class Config:
        from_attributes = True