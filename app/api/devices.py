from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.device import DeviceCreate, DeviceResponse
from app.services.device_service import (
    register_device,
    get_user_devices,
    trust_device,
    revoke_device_trust,
)
from app.security.dependencies import get_current_user
from app.models.user import User


router = APIRouter(
    prefix="/devices",
    tags=["Devices"],
)


@router.get("/", response_model=list[DeviceResponse])
def get_devices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_devices(db=db, user_id=current_user.id)


@router.post("/register", response_model=DeviceResponse)
def register_new_device(
    device: DeviceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return register_device(db=db, user_id=current_user.id, device=device)


@router.post("/{device_id}/trust", response_model=DeviceResponse)
def trust_user_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return trust_device(
        db=db,
        user_id=current_user.id,
        device_id=device_id,
    )


@router.post("/{device_id}/revoke", response_model=DeviceResponse)
def revoke_user_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return revoke_device_trust(
        db=db,
        user_id=current_user.id,
        device_id=device_id,
    )