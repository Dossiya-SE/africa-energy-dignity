"""SQLAlchemy persistence models for the AED registry."""
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    """Return an aware UTC timestamp."""
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Declarative SQLAlchemy base."""


class TimestampMixin:
    """Created and modified timestamps shared by mutable registry records."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class Institution(Base, TimestampMixin):
    __tablename__ = "institutions"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    institution_type: Mapped[str] = mapped_column(String(64))
    country_code: Mapped[str | None] = mapped_column(String(3))
    website: Mapped[str | None] = mapped_column(String(500))
    notes: Mapped[str | None] = mapped_column(Text)


class Geography(Base, TimestampMixin):
    __tablename__ = "geographies"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    level: Mapped[str] = mapped_column(String(64))
    parent_id: Mapped[str | None] = mapped_column(ForeignKey("geographies.id"))
    iso_code: Mapped[str | None] = mapped_column(String(16), unique=True)
    geometry_status: Mapped[str] = mapped_column(String(32), default="not_stored")


class Source(Base, TimestampMixin):
    __tablename__ = "sources"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    publisher_id: Mapped[str | None] = mapped_column(ForeignKey("institutions.id"))
    source_url: Mapped[str] = mapped_column(String(1000))
    access_date: Mapped[str] = mapped_column(String(10))
    temporal_coverage: Mapped[str | None] = mapped_column(String(255))
    geographic_coverage: Mapped[str | None] = mapped_column(String(255))
    licence: Mapped[str | None] = mapped_column(String(255))
    attribution: Mapped[str | None] = mapped_column(Text)
    limitations: Mapped[str | None] = mapped_column(Text)
    evidence_class: Mapped[str] = mapped_column(String(32), default="published")
    validation_status: Mapped[str] = mapped_column(String(32), default="proposed")
    checksum: Mapped[str | None] = mapped_column(String(128))


class Dataset(Base, TimestampMixin):
    __tablename__ = "datasets"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"))
    name: Mapped[str] = mapped_column(String(500))
    version: Mapped[str | None] = mapped_column(String(128))
    variable_definition: Mapped[str | None] = mapped_column(Text)
    unit: Mapped[str | None] = mapped_column(String(128))


class GeospatialAsset(Base, TimestampMixin):
    __tablename__ = "geospatial_assets"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    dataset_id: Mapped[str | None] = mapped_column(ForeignKey("datasets.id"))
    geography_id: Mapped[str | None] = mapped_column(ForeignKey("geographies.id"))
    name: Mapped[str] = mapped_column(String(500))
    asset_type: Mapped[str] = mapped_column(String(64))
    uri: Mapped[str] = mapped_column(String(1000))
    spatial_resolution: Mapped[str | None] = mapped_column(String(255))
    temporal_coverage: Mapped[str | None] = mapped_column(String(255))
    licence: Mapped[str | None] = mapped_column(String(255))
    validation_status: Mapped[str] = mapped_column(String(32), default="proposed")
    is_sensitive: Mapped[bool] = mapped_column(Boolean, default=False)


class Project(Base, TimestampMixin):
    __tablename__ = "projects"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(500))
    geography_id: Mapped[str | None] = mapped_column(ForeignKey("geographies.id"))
    project_status: Mapped[str] = mapped_column(String(32), default="synthetic")
    description: Mapped[str | None] = mapped_column(Text)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True)


class ProcessingRun(Base):
    __tablename__ = "processing_runs"
    id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=lambda: str(uuid4())
    )
    process_name: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32))
    code_commit: Mapped[str | None] = mapped_column(String(64))
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ValidationEvent(Base):
    __tablename__ = "validation_events"
    id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=lambda: str(uuid4())
    )
    entity_type: Mapped[str] = mapped_column(String(64))
    entity_id: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32))
    message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class AuditEvent(Base):
    __tablename__ = "audit_events"
    __table_args__ = (UniqueConstraint("event_hash", name="uq_audit_event_hash"),)
    id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=lambda: str(uuid4())
    )
    actor: Mapped[str] = mapped_column(String(255), default="api-user")
    action: Mapped[str] = mapped_column(String(128))
    entity_type: Mapped[str] = mapped_column(String(64))
    entity_id: Mapped[str] = mapped_column(String(64))
    event_hash: Mapped[str] = mapped_column(String(64))
    payload: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
