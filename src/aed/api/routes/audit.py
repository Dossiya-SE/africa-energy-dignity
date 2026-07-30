"""Read-only audit endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from aed.audit.service import list_events
from aed.database.session import get_db
from aed.registry.models import AuditEventRead

router = APIRouter(tags=["audit"])


@router.get("/audit-events", response_model=list[AuditEventRead])
def audit_events(db: Session = Depends(get_db)):
    """Return immutable audit history."""
    return list_events(db)
