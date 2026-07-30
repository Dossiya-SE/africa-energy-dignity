"""DATA-001 registry and API verification."""
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from aed.api.main import app
from aed.database.models import AuditEvent, Base, Geography, Institution
from aed.database.session import get_db
from aed.registry.models import SourceCreate


@pytest.fixture()
def db_session(tmp_path: Path):
    """Provide an isolated SQLite database using production models."""
    engine = create_engine(
        f"sqlite+pysqlite:///{tmp_path / 'test.db'}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False
    )
    with session_factory() as session:
        yield session


@pytest.fixture()
def client(db_session: Session):
    """Override the API database with the isolated test session."""

    def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def valid_source(source_id: str = "SRC-TEST-001") -> dict:
    """Return complete synthetic source metadata."""
    return {
        "id": source_id,
        "title": "Controlled test source",
        "source_url": "https://example.org/source",
        "access_date": "2026-07-30",
        "temporal_coverage": "2025",
        "geographic_coverage": "Burkina Faso",
        "licence": "CC-BY-4.0",
        "attribution": "Example Publisher",
        "limitations": "Synthetic metadata used only for tests.",
        "evidence_class": "synthetic",
        "validation_status": "validated",
    }


def test_source_validation_accepts_complete_metadata():
    source = SourceCreate.model_validate(valid_source())
    assert source.validation_status == "validated"


def test_validated_source_requires_licence():
    payload = valid_source()
    payload["licence"] = None
    with pytest.raises(ValidationError, match="licence"):
        SourceCreate.model_validate(payload)


def test_institution_creation_and_audit(
    client: TestClient, db_session: Session
):
    response = client.post(
        "/institutions",
        json={
            "id": "BFA-TEST-INSTITUTION",
            "name": "Test Institution",
            "institution_type": "national_agency",
            "country_code": "BFA",
        },
    )
    assert response.status_code == 201
    assert db_session.get(Institution, "BFA-TEST-INSTITUTION") is not None
    count = db_session.scalar(select(func.count()).select_from(AuditEvent))
    assert count == 1


def test_geography_creation(client: TestClient, db_session: Session):
    response = client.post(
        "/geographies",
        json={
            "id": "GEO-BFA",
            "name": "Burkina Faso",
            "level": "country",
            "iso_code": "BFA",
        },
    )
    assert response.status_code == 201
    assert db_session.get(Geography, "GEO-BFA") is not None


def test_duplicate_identifier_rejected(client: TestClient):
    payload = {
        "id": "GEO-BFA",
        "name": "Burkina Faso",
        "level": "country",
        "iso_code": "BFA",
    }
    assert client.post("/geographies", json=payload).status_code == 201
    assert client.post("/geographies", json=payload).status_code == 409


def test_api_health(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_source_creation(client: TestClient):
    created = client.post("/sources", json=valid_source())
    assert created.status_code == 201
    assert created.json()["validation_status"] == "validated"


def test_api_source_retrieval(client: TestClient):
    payload = valid_source()
    assert client.post("/sources", json=payload).status_code == 201
    retrieved = client.get(f"/sources/{payload['id']}")
    assert retrieved.status_code == 200
    assert retrieved.json()["licence"] == "CC-BY-4.0"


def test_audit_events_are_created(client: TestClient):
    client.post("/sources", json=valid_source())
    events = client.get("/audit-events")
    assert events.status_code == 200
    assert events.json()[0]["entity_type"] == "source"


def test_database_migration(tmp_path: Path):
    database_path = tmp_path / "migration.db"
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
