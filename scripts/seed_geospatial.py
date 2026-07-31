"""Seed or update controlled GEO-002 geospatial evidence records."""
from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter
from sqlalchemy.orm import Session

from aed.database.models import (
    Dataset,
    GeospatialAsset,
    Geography,
    ProcessingRun,
    Source,
    ValidationEvent,
)
from aed.database.session import engine
from aed.geospatial.integrity import validate_boundary_geojson
from aed.registry.models import SourceCreate

FIXTURE = Path("data/fixtures/geospatial_seed.json")
BOUNDARY = Path("data/canonical/boundaries/bfa-natural-earth-5.1.1.geojson")


def _source_values(raw: dict[str, Any]) -> dict[str, Any]:
    payload = TypeAdapter(SourceCreate).validate_python(raw)
    values = payload.model_dump(mode="python")
    values["source_url"] = str(payload.source_url) if payload.source_url else None
    values["temporal_coverage"] = payload.temporal_coverage.model_dump(
        mode="json", exclude_none=True
    )
    return values


def _dated(raw: dict[str, Any]) -> dict[str, Any]:
    values = dict(raw)
    for field in ("started_at", "completed_at", "created_at"):
        if values.get(field):
            values[field] = datetime.fromisoformat(values[field])
    return values


def _normalized(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def _upsert(db: Session, model, values: dict[str, Any]) -> None:
    record = db.get(model, values["id"])
    if record is None:
        db.add(model(**values))
        return
    for field, value in values.items():
        if _normalized(getattr(record, field)) != _normalized(value):
            setattr(record, field, value)


def seed_with_session(db: Session, root: Path = Path(".")) -> None:
    """Load the complete source-to-validation chain idempotently."""
    records = json.loads((root / FIXTURE).read_text(encoding="utf-8"))
    validate_boundary_geojson(root / BOUNDARY)

    geography = db.get(Geography, "geo.bfa")
    if geography is None:
        geography = Geography(
            id="geo.bfa",
            name="Burkina Faso",
            level="country",
            iso_code="BFA",
            geometry_status="validated",
        )
        db.add(geography)
    else:
        geography.geometry_status = "validated"
    db.flush()

    for raw in records["sources"]:
        _upsert(db, Source, _source_values(raw))
    db.flush()
    for raw in records["datasets"]:
        _upsert(db, Dataset, dict(raw))
    db.flush()
    for raw in records["processing_runs"]:
        _upsert(db, ProcessingRun, _dated(raw))
    db.flush()
    for raw in records["assets"]:
        _upsert(db, GeospatialAsset, dict(raw))
    db.flush()
    for raw in records["validation_events"]:
        _upsert(db, ValidationEvent, _dated(raw))
    db.commit()


def seed() -> None:
    """Seed GEO-002 evidence into the configured database."""
    with Session(engine) as db:
        seed_with_session(db)


if __name__ == "__main__":
    seed()
