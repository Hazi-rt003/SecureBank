import logging

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog

logger = logging.getLogger("securebank.audit")


def log_event(
    db: Session,
    user_id: int | None,
    action: str,
    details: str | None = None,
    ip_address: str | None = None,
    device_fingerprint: str | None = None,
) -> None:
    """
    Writes an audit trail entry. Deliberately never raises, same philosophy
    as email/push notifications — a failure to record history must not
    block the actual action being recorded.
    """
    try:
        entry = AuditLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=ip_address,
            device_fingerprint=device_fingerprint,
        )
        db.add(entry)
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Failed to write audit log | action=%s user_id=%s", action, user_id)


def get_user_audit_logs(db: Session, user_id: int, limit: int = 100) -> list[AuditLog]:
    return (
        db.query(AuditLog)
        .filter(AuditLog.user_id == user_id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .all()
    )