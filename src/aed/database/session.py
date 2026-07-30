"""Database engine and session lifecycle."""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from aed.settings import get_settings


def build_engine(url: str | None = None):
    """Build an engine for PostgreSQL or deterministic SQLite tests."""
    settings = get_settings()
    database_url = url or settings.database_url
    kwargs = {"pool_pre_ping": True}
    if database_url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(database_url, echo=settings.database_echo, **kwargs)


engine = build_engine()
SessionLocal = sessionmaker(
    bind=engine, autoflush=False, expire_on_commit=False
)


def get_db() -> Generator[Session, None, None]:
    """Provide one transactional SQLAlchemy session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
