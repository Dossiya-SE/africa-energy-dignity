"""Seed controlled DATA-001 records without unverified numerical claims."""
import json
from pathlib import Path

from sqlalchemy.orm import Session

from aed.audit.service import record_event
from aed.database.models import Geography, Institution, Project, Source
from aed.database.session import engine

FIXTURE = Path("data/fixtures/registry_seed.json")
MODEL_MAP = {
    "institutions": Institution,
    "geographies": Geography,
    "sources": Source,
    "projects": Project,
}


def seed() -> None:
    """Load idempotent controlled fixtures after Alembic migration."""
    records = json.loads(FIXTURE.read_text(encoding="utf-8"))
    with Session(engine) as db:
        for group, model in MODEL_MAP.items():
            for values in records[group]:
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
