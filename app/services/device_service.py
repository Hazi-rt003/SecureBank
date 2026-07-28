from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.device import Device
from app.schemas.device import DeviceCreate


def register_device(
    db: Session,
    user_id: int,
    device: DeviceCreate,
):
    # Check if device_id already exists
    existing_device = (
        db.query(Device)
        .filter(Device.device_id == device.device_id)
        .first()
    )

    if existing_device:
        raise HTTPException(
            status_code=400,
            detail="Device is already registered.",
        )

    # Check if device fingerprint already exists
    existing_fingerprint = (
        db.query(Device)
        .filter(
            Device.device_fingerprint
            == device.device_fingerprint
        )
        .first()
    )

    if existing_fingerprint:
        raise HTTPException(
            status_code=400,
            detail="Device fingerprint is already registered.",
        )

    new_device = Device(
        user_id=user_id,
        device_name=device.device_name,
        device_id=device.device_id,
        device_type=device.device_type,
        device_fingerprint=device.device_fingerprint,
        platform=device.platform,
        trusted=False,
    )

    db.add(new_device)
    db.commit()
    db.refresh(new_device)

    return new_device