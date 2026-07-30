"""Seed controlled DATA-001 records without unverified numerical claims."""
import json
from pathlib import Path

from pydantic import TypeAdapter
from sqlalchemy.orm import Session

from aed.audit.service import record_event
from aed.database.models import Geography, Institution, Project, Source
from aed.database.session import engine
from aed.registry.models import (
    GeographyCreate,
    InstitutionCreate,
    ProjectCreate,
    SourceCreate,
)

FIXTURE = Path("data/fixtures/registry_seed.json")
MODEL_MAP = {
    "institutions": (Institution, InstitutionCreate),
    "geographies": (Geography, GeographyCreate),
    "sources": (Source, SourceCreate),
    "projects": (Project, ProjectCreate),
}


def normalized_values(schema, raw: dict) -> dict:
    """Validate fixture input and convert it to persistence-native values."""
    payload = TypeAdapter(schema).validate_python(raw)
    values = payload.model_dump(mode="python")
    if isinstance(payload, SourceCreate):
        values["source_url"] = str(payload.source_url) if payload.source_url else None
        values["temporal_coverage"] = payload.temporal_coverage.model_dump(
            mode="json", exclude_none=True
        )
    elif isinstance(payload, InstitutionCreate):
        values["website"] = str(payload.website) if payload.website else None
    return values


def seed() -> None:
    """Load idempotent controlled fixtures after Alembic migration."""
    records = json.loads(FIXTURE.read_text(encoding="utf-8"))
    with Session(engine) as db:
        for group, (model, schema) in MODEL_MAP.items():
            for raw_values in records[group]:
                values = normalized_values(schema, raw_values)
                if db.get(model, values["id"]) is not None:
                    continue
                db.add(model(**values))
                record_event(
                    db,
                    action="seed",
                    entity_type=model.__tablename__,
                    entity_id=values["id"],
                    payload=values,
                    actor="seed-script",
                )
        db.commit()


if __name__ == "__main__":
    seed()
