"""API contract tests for the executable AED registry."""
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine


def institution_payload() -> dict:
    return {
        "id": "institution.aber",
        "name": "Agence Burkinabè de l'Électrification Rurale",
        "institution_type": "national_agency",
        "country_code": "BFA",
        "website": "https://www.aber.bf",
        "notes": "Controlled test record.",
    }


def source_payload() -> dict:
    return {
        "id": "source.bfa.population.candidate",
        "title": "Candidate Burkina Faso population source",
        "original_publisher": "Publisher pending original-product verification",
        "publisher_id": None,
        "source_url": "https://www.worldpop.org",
        "persistent_identifier": None,
        "archive_reference": None,
        "access_date": "2026-07-30",
        "temporal_coverage": {
            "description": "Population product year not yet selected."
        },
        "geographic_coverage": ["geo.bfa"],
        "licence": "licence_unknown",
        "attribution_requirements": "Pending product-specific verification.",
        "access_method": "Public website candidate.",
        "known_limitations": [
            "Product year, model, resolution and licence require verification."
        ],
        "evidence_class": "unverified",
        "verification_status": "proposed",
        "responsible_reviewer": "Dossiya Dakou",
        "version": "0.1",
        "checksum": None,
    }


def test_health_and_readiness(client):
    health = client.get("/health")
    ready = client.get("/ready")

    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert ready.status_code == 200
    assert ready.json() == {"status": "ready", "database": "reachable"}


def test_institution_creation_is_audited_and_duplicate_safe(client):
    created = client.post("/institutions", json=institution_payload())
    duplicate = client.post("/institutions", json=institution_payload())
    audit = client.get("/audit-events")

    assert created.status_code == 201
    assert created.json()["id"] == "institution.aber"
    assert duplicate.status_code == 409
    assert audit.status_code == 200
    events = audit.json()
    assert len(events) == 1
    assert events[0]["entity_type"] == "institution"
    assert events[0]["entity_id"] == "institution.aber"
    assert events[0]["action"] == "create"


def test_geography_creation_and_duplicate_identifier_rejection(client):
    payload = {
        "id": "geo.bfa",
        "name": "Burkina Faso",
        "level": "country",
        "iso_code": "BFA",
    }
    assert client.post("/geographies", json=payload).status_code == 201
    assert client.post("/geographies", json=payload).status_code == 409


def test_source_creation_and_retrieval_preserve_canonical_metadata(client):
    payload = source_payload()
    created = client.post("/sources", json=payload)
    retrieved = client.get(f"/sources/{payload['id']}")

    assert created.status_code == 201, created.text
    assert retrieved.status_code == 200
    body = retrieved.json()
    assert body["original_publisher"] == payload["original_publisher"]
    assert body["geographic_coverage"] == ["geo.bfa"]
    assert body["temporal_coverage"]["description"].startswith("Population")
    assert body["licence"] == "licence_unknown"
    assert body["evidence_class"] == "unverified"
    assert body["verification_status"] == "proposed"


def test_unknown_source_returns_404(client):
    response = client.get("/sources/source.missing")
    assert response.status_code == 404


def test_source_requires_provenance_and_licensing_fields(client):
    payload = source_payload()
    del payload["licence"]
    response = client.post("/sources", json=payload)
    assert response.status_code == 422


def test_unverified_source_cannot_be_upgraded_to_verified_state(client):
    payload = source_payload()
    payload["verification_status"] = "source_verified"
    response = client.post("/sources", json=payload)
    assert response.status_code == 422


def test_temporal_interval_is_mathematically_ordered(client):
    payload = source_payload()
    payload["temporal_coverage"] = {
        "valid_from": "2026-12-31",
        "valid_to": "2026-01-01",
    }
    response = client.post("/sources", json=payload)
    assert response.status_code == 422


def test_database_migration_from_empty_database(tmp_path: Path, monkeypatch):
    database_path = tmp_path / "migration.db"
    monkeypatch.delenv("AED_DATABASE_URL", raising=False)
    config = Config("alembic.ini")
    config.set_main_option(
        "sqlalchemy.url", f"sqlite+pysqlite:///{database_path}"
    )
    command.upgrade(config, "head")
    engine = create_engine(f"sqlite+pysqlite:///{database_path}")
    with engine.connect() as connection:
        table_names = set(connection.dialect.get_table_names(connection))
    assert {
        "institutions",
        "geographies",
        "sources",
        "datasets",
        "geospatial_assets",
        "projects",
        "processing_runs",
        "validation_events",
        "audit_events",
    }.issubset(table_names)
