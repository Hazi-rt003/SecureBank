import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.device import DeviceResponse
from app.security.dependencies import get_current_user
from app.services.passkey_service import (
    start_device_trust_registration,
    finish_device_trust_registration,
)

router = APIRouter(prefix="/devices", tags=["Passkeys"])


@router.get("/{device_id}/trust/passkey/options")
def get_passkey_registration_options(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    options_json = start_device_trust_registration(db, current_user, device_id)
    # options_to_json() from the webauthn lib already returns a JSON string —
    # decode it so FastAPI serializes it as a proper JSON object, not a JSON string.
    return json.loads(options_json)


@router.post("/{device_id}/trust/passkey/verify", response_model=DeviceResponse)
def verify_passkey_registration(
    device_id: int,
    credential: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return finish_device_trust_registration(db, current_user, device_id, credential)