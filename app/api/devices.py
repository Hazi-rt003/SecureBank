from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.device import DeviceCreate, DeviceResponse
from app.services.device_service import register_device
from app.security.dependencies import get_current_user
from app.models.user import User


router = APIRouter(
    prefix="/devices",
    tags=["Devices"],
)


@router.post(
    "/register",
    response_model=DeviceResponse,
)
def register_new_device(
    device: DeviceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return register_device(
        db=db,
        user_id=current_user.id,
        device=device,
    )