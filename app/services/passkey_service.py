import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from webauthn import (
    generate_registration_options,
    verify_registration_response,
    options_to_json,
)
from webauthn.helpers import bytes_to_base64url, base64url_to_bytes
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
)

from app.models.device import Device
from app.models.passkey_credential import PasskeyCredential
from app.models.webauthn_challenge import WebAuthnChallenge
from app.models.user import User

load_dotenv()

# NOTE: RP_ID must exactly match the domain in the browser's address bar
# ("localhost" works for dev; production needs your real domain, over HTTPS).
# ORIGIN must be the exact scheme+host+port the browser is using.
RP_ID = os.getenv("WEBAUTHN_RP_ID", "localhost")
RP_NAME = os.getenv("WEBAUTHN_RP_NAME", "SecureBank")
ORIGIN = os.getenv("WEBAUTHN_ORIGIN", "http://localhost:8000")

CHALLENGE_TTL_MINUTES = 5


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


def start_device_trust_registration(db: Session, user: User, device_id: int) -> str:
    """
    Step 1 of the ceremony: issue a challenge for the browser to sign with
    a new passkey. Returns the options as a JSON string ready to send
    straight to the client (matches what navigator.credentials.create() needs).
    """
    _get_owned_device(db, user.id, device_id)

    options = generate_registration_options(
        rp_id=RP_ID,
        rp_name=RP_NAME,
        user_id=str(user.id).encode("utf-8"),
        user_name=user.email,
        user_display_name=user.full_name,
        authenticator_selection=AuthenticatorSelectionCriteria(
            user_verification=UserVerificationRequirement.PREFERRED,
        ),
    )

    # Drop any stale pending challenge for this user/device before storing the new one.
    db.query(WebAuthnChallenge).filter(
        WebAuthnChallenge.user_id == user.id,
        WebAuthnChallenge.device_id == device_id,
        WebAuthnChallenge.purpose == "registration",
    ).delete()

    db.add(
        WebAuthnChallenge(
            user_id=user.id,
            device_id=device_id,
            challenge=bytes_to_base64url(options.challenge),
            purpose="registration",
        )
    )
    db.commit()

    return options_to_json(options)


def finish_device_trust_registration(
    db: Session, user: User, device_id: int, credential: dict
) -> Device:
    """
    Step 2 of the ceremony: verify what the browser signed, store the
    resulting public key, and mark the device trusted.
    """
    device = _get_owned_device(db, user.id, device_id)

    challenge_row = (
        db.query(WebAuthnChallenge)
        .filter(
            WebAuthnChallenge.user_id == user.id,
            WebAuthnChallenge.device_id == device_id,
            WebAuthnChallenge.purpose == "registration",
        )
        .order_by(WebAuthnChallenge.created_at.desc())
        .first()
    )

    if not challenge_row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending passkey registration for this device. Request options again.",
        )

    created_at = challenge_row.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) - created_at > timedelta(minutes=CHALLENGE_TTL_MINUTES):
        db.delete(challenge_row)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passkey registration challenge expired. Request options again.",
        )

    try:
        verification = verify_registration_response(
            credential=credential,
            expected_challenge=base64url_to_bytes(challenge_row.challenge),
            expected_rp_id=RP_ID,
            expected_origin=ORIGIN,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Passkey verification failed: {exc}",
        )

    db.add(
        PasskeyCredential(
            user_id=user.id,
            device_id=device_id,
            credential_id=bytes_to_base64url(verification.credential_id),
            public_key=verification.credential_public_key,
            sign_count=verification.sign_count,
        )
    )

    device.trusted = True

    db.delete(challenge_row)
    db.commit()
    db.refresh(device)

    return device