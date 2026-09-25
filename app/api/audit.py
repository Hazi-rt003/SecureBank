from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.audit_log import AuditLogResponse
from app.security.dependencies import get_current_user
from app.services.audit_service import get_user_audit_logs

router = APIRouter(prefix="/audit-logs", tags=["Audit"])


@router.get("/", response_model=list[AuditLogResponse])
def list_my_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_audit_logs(db, current_user.id)