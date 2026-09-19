from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.device import Device
from app.schemas.device import DeviceCreate


def get_user_devices(db: Session, user_id: int) -> list[Device]:
    return db.query(Device).filter(Device.user_id == user_id).all()


def get_device_by_fingerprint(
    db: Session, user_id: int, device_fingerprint: str
) -> Device | None:
    return (
        db.query(Device)
        .filter(
            Device.user_id == user_id,
            Device.device_fingerprint == device_fingerprint,
        )
        .first()
    )


def register_device(db: Session, user_id: int, device: DeviceCreate) -> Device:
    # Re-registering a known fingerprint just returns the existing record
    # instead of erroring or creating a duplicate.
    existing = get_device_by_fingerprint(db, user_id, device.device_fingerprint)
    if existing:
        return existing

    db_device = Device(
        user_id=user_id,
        device_name=device.device_name,
        device_id=device.device_id,
        device_type=device.device_type,
        device_fingerprint=device.device_fingerprint,
        platform=device.platform,
        trusted=False,  # new devices always start untrusted
    )
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def _get_owned_device(db: Session, user_id: int, device_id: int) -> Device:
    device = (
        db.query(Device)
        .filter(Device.id == device_id, Device.user_id == user_id)
        .first()
    )
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )
    return device


def trust_device(db: Session, user_id: int, device_id: int) -> Device:
    device = _get_owned_device(db, user_id, device_id)
    device.trusted = True
    db.commit()
    db.refresh(device)
    return device


def revoke_device_trust(db: Session, user_id: int, device_id: int) -> Device:
    device = _get_owned_device(db, user_id, device_id)
    device.trusted = False
    db.commit()
    db.refresh(device)
    return device