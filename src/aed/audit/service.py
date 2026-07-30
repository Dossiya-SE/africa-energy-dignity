"""Append-only audit-event service."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from aed.audit.events import canonical_payload, event_hash
from aed.database.models import AuditEvent


def record_event(
    db: Session,
    *,
    action: str,
    entity_type: str,
    entity_id: str,
    payload: dict,
    actor: str = "api-user",
) -> AuditEvent:
    """Append one immutable audit event to the current transaction."""
    event = AuditEvent(
        actor=actor,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        payload=canonical_payload(payload),
        event_hash=event_hash(
            actor=actor,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            payload=payload,
        ),
    )
    db.add(event)
    db.flush()
    return event


def list_events(db: Session) -> list[AuditEvent]:
    """Return audit history in append order."""
    statement = select(AuditEvent).order_by(
        AuditEvent.created_at, AuditEvent.id
    )
    return list(db.scalars(statement).all())
