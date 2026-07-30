"""Shared fixtures for deterministic DATA-001 API tests."""
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from aed.api.main import app
from aed.database.models import Base
from aed.database.session import get_db


@pytest.fixture
def db_session(tmp_path) -> Generator[Session, None, None]:
    """Create an isolated relational database for each test."""
    database_path = tmp_path / "test-registry.db"
    engine = create_engine(
        f"sqlite+pysqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    local_session = sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False
    )
    with local_session() as session:
        yield session
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Run the FastAPI application against the isolated test transaction."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
