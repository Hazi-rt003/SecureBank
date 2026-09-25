from typing import Union

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from app.core.limiter import limiter

from app.database.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import create_user, login_user, complete_passkey_login

from app.models.user import User
from app.models.session import UserSession
from app.security.dependencies import get_current_user, get_current_session

from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.auth import Token, LoginStepUpResponse, PasskeyLoginVerifyRequest
from app.schemas.session import SessionResponse
from app.services.session_service import (
    get_user_sessions,
    revoke_session,
    revoke_other_sessions,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/me")
def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "phone_number": current_user.phone_number,
        "is_verified": current_user.is_verified,
    }


@router.post("/register", response_model=UserResponse)
@limiter.limit("3/hour")
def register_user(
    request: Request,
    user: UserCreate,
    db: Session = Depends(get_db)):

    return create_user(db, user)

@router.post(
    "/login",
    response_model=Union[Token, LoginStepUpResponse],
)
@limiter.limit("5/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    device_fingerprint: str | None = Header(default=None, alias="X-Device-Fingerprint"),
    device_id: str | None = Header(default=None, alias="X-Device-Id"),
    device_name: str | None = Header(default=None, alias="X-Device-Name"),
    device_type: str | None = Header(default=None, alias="X-Device-Type"),
    platform: str | None = Header(default=None, alias="X-Platform"),
):
    return login_user(
        db,
        form_data.username,
        form_data.password,
        device_fingerprint=device_fingerprint,
        device_id=device_id,
        device_name=device_name,
        device_type=device_type,
        platform=platform,
    )


@router.post(
    "/login/passkey/verify",
    response_model=Token,
)
def login_passkey_verify(
    payload: PasskeyLoginVerifyRequest,
    db: Session = Depends(get_db),
):
    return complete_passkey_login(db, payload.credential)


@router.get("/sessions", response_model=list[SessionResponse])
def list_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_session: UserSession = Depends(get_current_session),
):
    sessions = get_user_sessions(db, current_user.id)
    return [
        SessionResponse.model_validate(s).model_copy(
            update={"is_current": s.id == current_session.id}
        )
        for s in sessions
    ]


@router.post("/sessions/{session_id}/revoke", response_model=SessionResponse)
def revoke_one_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return revoke_session(db, current_user.id, session_id)


@router.post("/sessions/revoke-others")
def revoke_others(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_session: UserSession = Depends(get_current_session),
):
    count = revoke_other_sessions(db, current_user.id, current_session.id)
    return {"revoked_count": count}


@router.post("/logout")
def logout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_session: UserSession = Depends(get_current_session),
):
    revoke_session(db, current_user.id, current_session.id)
    return {"detail": "Logged out"}