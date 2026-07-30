"""Seed verified and publication-blocked GEO-002 records idempotently."""
import json
from datetime import datetime, timezone
from pathlib import Path

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
RUN_ID = "run.bfa.boundary.natural-earth.v5.1.1"
VALIDATION_ID = "validation.asset.bfa.boundary.natural-earth.v5.1.1"


def _source_values(raw: dict) -> dict:
    payload = TypeAdapter(SourceCreate).validate_python(raw)
    values = payload.model_dump(mode="python")
    values["source_url"] = str(payload.source_url) if payload.source_url else None
    values["temporal_coverage"] = payload.temporal_coverage.model_dump(
        mode="json", exclude_none=True
    )
    return values


def seed_with_session(db: Session, root: Path = Path(".")) -> None:
    records = json.loads((root / FIXTURE).read_text(encoding="utf-8"))
    boundary = validate_boundary_geojson(root / BOUNDARY)
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
        values = _source_values(raw)
        if db.get(Source, values["id"]) is None:
            db.add(Source(**values))
    db.flush()
    for raw in records["datasets"]:
        if db.get(Dataset, raw["id"]) is None:
            db.add(Dataset(**raw))
    if db.get(ProcessingRun, RUN_ID) is None:
        db.add(
            ProcessingRun(
                id=RUN_ID,
                process_name="extract-natural-earth-bfa-admin0",
                status="completed",
                code_commit="GEO-002",
                input_checksum="git-sha1:1e6ab74c7042f97013be69ceec798be8e1aff27d",
                output_checksum=f"sha256:{boundary.checksum}",
                parameters_json={"selector": "ADM0_A3=BFA", "output_crs": "OGC:CRS84"},
                started_at=datetime(2026, 7, 30, tzinfo=timezone.utc),
                completed_at=datetime(2026, 7, 30, tzinfo=timezone.utc),
            )
        )
    db.flush()
    for raw in records["assets"]:
        if db.get(GeospatialAsset, raw["id"]) is None:
            db.add(GeospatialAsset(**raw))
    if db.get(ValidationEvent, VALIDATION_ID) is None:
        db.add(
            ValidationEvent(
                id=VALIDATION_ID,
                entity_type="geospatial_asset",
                entity_id="asset.bfa.boundary.natural-earth.v5.1.1",
                status="validated",
                message="Checksum, CRS, ISO identity, geometry validity and national extent passed.",
                checks_json={
                    "checksum": boundary.checksum,
                    "crs": boundary.crs,
                    "bbox": list(boundary.bbox),
                    "geometry_type": boundary.geometry_type,
                    "iso_a3": "BFA",
                },
            )
        )
    db.commit()


def seed() -> None:
    with Session(engine) as db:
        seed_with_session(db)


if __name__ == "__main__":
    seed()
