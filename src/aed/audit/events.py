"""Deterministic audit event hashing."""
import hashlib
import json


def canonical_payload(payload: dict) -> str:
    """Serialize an audit payload deterministically."""
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), default=str
    )


def event_hash(
    *,
    actor: str,
    action: str,
    entity_type: str,
    entity_id: str,
    payload: dict,
) -> str:
    """Hash the immutable content of an audit event."""
    material = "|".join(
        [actor, action, entity_type, entity_id, canonical_payload(payload)]
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()
