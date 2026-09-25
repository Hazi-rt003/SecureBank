import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.models.session import UserSession
from app.security.jwt import ACCESS_TOKEN_EXPIRE_MINUTES


def create_session(
    db: DBSession, user_id: int, device_id: int | None
) -> tuple[str, UserSession]:
    jti = uuid.uuid4().hex
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    session = UserSession(
        user_id=user_id,
        device_id=device_id,
        jti=jti,
        expires_at=expires_at,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return jti, session


def get_user_sessions(db: DBSession, user_id: int) -> list[UserSession]:
    return (
        db.query(UserSession)
        .filter(UserSession.user_id == user_id)
        .order_by(UserSession.created_at.desc())
        .all()
    )


def _get_owned_session(db: DBSession, user_id: int, session_id: int) -> UserSession:
    session = (
        db.query(UserSession)
        .filter(UserSession.id == session_id, UserSession.user_id == user_id)
        .first()
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    return session


def revoke_session(db: DBSession, user_id: int, session_id: int) -> UserSession:
    session = _get_owned_session(db, user_id, session_id)
    if session.revoked_at is None:
        session.revoked_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(session)
    return session


def revoke_other_sessions(db: DBSession, user_id: int, current_session_id: int) -> int:
    now = datetime.now(timezone.utc)
    sessions = (
        db.query(UserSession)
        .filter(
            UserSession.user_id == user_id,
            UserSession.id != current_session_id,
            UserSession.revoked_at.is_(None),
        )
        .all()
    )
    for s in sessions:
        s.revoked_at = now
    db.commit()
    return len(sessions)