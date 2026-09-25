import json
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.schemas.auth import Token
from app.schemas.device import DeviceCreate
from app.security.password import hash_password, verify_password
from app.security.jwt import create_access_token
from app.services.device_service import get_device_by_fingerprint, register_device
from app.services.account_service import create_account_for_user
from app.services.notification_service import notify_login
from app.services.session_service import create_session
from app.services.audit_service import log_event
from app.services.passkey_service import (
    get_device_credentials,
    start_login_authentication,
    finish_login_authentication,
)


def create_user(db: Session, user: UserCreate) -> User:
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    db_user = User(
        full_name=user.full_name,
        email=user.email,
        phone_number=user.phone_number,
        password_hash=hash_password(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Every new user gets an account (seeded with a demo balance — see
    # account_service for why; there's no real deposit flow yet).
    create_account_for_user(db, db_user.id)

    log_event(db, user_id=db_user.id, action="register", details=f"email={db_user.email}")

    return db_user


def login_user(
    db: Session,
    email: str,
    password: str,
    device_fingerprint: str | None = None,
    device_id: str | None = None,
    device_name: str | None = None,
    device_type: str | None = None,
    platform: str | None = None,
):
    # form_data.username is passed in as `email` from users.py's /login route
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        log_event(
            db,
            user_id=user.id if user else None,
            action="login_failed",
            details=f"email={email}",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    device_trusted: bool | None = None
    new_device: bool | None = None
    device = None

    if device_fingerprint:
        device = get_device_by_fingerprint(db, user.id, device_fingerprint)

        if device is None and device_id and device_name and platform:
            # First time we've seen this device from this user — register
            # it untrusted rather than silently accepting it as trusted.
            device = register_device(
                db=db,
                user_id=user.id,
                device=DeviceCreate(
                    device_name=device_name,
                    device_id=device_id,
                    device_type=device_type or "unknown",
                    device_fingerprint=device_fingerprint,
                    platform=platform,
                ),
            )
            new_device = True
        elif device is not None:
            new_device = False

        if device is not None:
            device_trusted = device.trusted

            # Step-up: a device with a registered passkey can't finish login
            # on password alone — hand back a challenge instead of a token.
            # Gated on "has a credential", not the `trusted` flag, so the old
            # manual /trust fallback (no credential) doesn't trigger this.
            credentials = get_device_credentials(db, device.id)
            if credentials:
                options_json = start_login_authentication(db, user.id, device.id)
                notify_login(
                    user=user,
                    device_fingerprint=device_fingerprint,
                    trusted=True,
                    new_device=False,
                )
                return {
                    "step_up_required": True,
                    "device_id": device.id,
                    "options": json.loads(options_json),
                }

            # No passkey on this device — finish the single-factor login as before.
            device.last_seen = datetime.now(timezone.utc)
            db.commit()

        notify_login(
            user=user,
            device_fingerprint=device_fingerprint,
            trusted=bool(device_trusted),
            new_device=bool(new_device),
        )

    jti, _session = create_session(db, user_id=user.id, device_id=device.id if device else None)
    access_token = create_access_token(data={"sub": str(user.id), "jti": jti})

    log_event(
        db,
        user_id=user.id,
        action="login_success",
        details=f"device_fingerprint={device_fingerprint}",
        device_fingerprint=device_fingerprint,
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        device_trusted=device_trusted,
        new_device=new_device,
    )


def complete_passkey_login(db: Session, credential: dict) -> Token:
    user_id, device_id = finish_login_authentication(db, credential)

    jti, _session = create_session(db, user_id=user_id, device_id=device_id)
    access_token = create_access_token(data={"sub": str(user_id), "jti": jti})

    log_event(
        db,
        user_id=user_id,
        action="login_success",
        details="via passkey step-up",
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        device_trusted=True,
        new_device=False,
    )