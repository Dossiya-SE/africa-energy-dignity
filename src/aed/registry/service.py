"""Transactional registry operations."""
from sqlalchemy.orm import Session

from aed.audit.service import record_event
from aed.registry.repository import create_record


def create_with_audit(
    db: Session,
    *,
    model,
    entity_type: str,
    values: dict,
):
    """Create a registry record and its audit event atomically."""
    record = create_record(db, model, values)
    record_event(
        db,
        action="create",
        entity_type=entity_type,
        entity_id=record.id,
        payload=values,
    )
    db.commit()
    db.refresh(record)
    return record
