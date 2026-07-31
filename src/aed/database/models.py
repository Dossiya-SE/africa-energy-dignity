"""SQLAlchemy persistence models for the AED registry."""
from datetime import date, datetime, timezone
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    event,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Declarative SQLAlchemy base."""


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
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
    """Canonical source view over the forward-compatible registry table."""

    __tablename__ = "sources"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    original_publisher: Mapped[str] = mapped_column(String(500))
    publisher_id: Mapped[str | None] = mapped_column(ForeignKey("institutions.id"))
    source_url: Mapped[str | None] = mapped_column(String(1000))
    persistent_identifier: Mapped[str | None] = mapped_column(String(500))
    archive_reference: Mapped[str | None] = mapped_column(String(500))
    access_date: Mapped[date] = mapped_column("access_date_value", Date)
    temporal_coverage: Mapped[dict] = mapped_column("temporal_coverage_json", JSON)
    geographic_coverage: Mapped[list] = mapped_column("geographic_coverage_json", JSON)
    licence: Mapped[str] = mapped_column(String(255))
    attribution_requirements: Mapped[str] = mapped_column(Text)
    access_method: Mapped[str] = mapped_column(String(255))
    known_limitations: Mapped[list] = mapped_column("known_limitations_json", JSON)
    evidence_class: Mapped[str] = mapped_column(String(32), default="published")
    verification_status: Mapped[str] = mapped_column(String(32), default="proposed")
    responsible_reviewer: Mapped[str] = mapped_column(String(255))
    version: Mapped[str] = mapped_column("source_version", String(128))
    checksum: Mapped[str | None] = mapped_column(String(128))


class Dataset(Base, TimestampMixin):
    __tablename__ = "datasets"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"))
    name: Mapped[str] = mapped_column(String(500))
    version: Mapped[str | None] = mapped_column(String(128))
    variable_definition: Mapped[str | None] = mapped_column(Text)
    unit: Mapped[str | None] = mapped_column(String(128))
    original_uri: Mapped[str | None] = mapped_column(String(1000))
    checksum: Mapped[str | None] = mapped_column(String(128))
    media_type: Mapped[str | None] = mapped_column(String(128))
    metadata_json: Mapped[dict | None] = mapped_column(JSON)
    validation_status: Mapped[str] = mapped_column(String(32), default="proposed")


class ProcessingRun(Base):
    __tablename__ = "processing_runs"
    id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=lambda: str(uuid4())
    )
    process_name: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32))
    code_commit: Mapped[str | None] = mapped_column(String(64))
    input_checksum: Mapped[str | None] = mapped_column(String(128))
    output_checksum: Mapped[str | None] = mapped_column(String(128))
    parameters_json: Mapped[dict | None] = mapped_column(JSON)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


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
    checksum: Mapped[str | None] = mapped_column(String(128))
    crs: Mapped[str | None] = mapped_column(String(128))
    bbox: Mapped[list | None] = mapped_column("bbox_json", JSON)
    nodata: Mapped[dict | None] = mapped_column("nodata_json", JSON)
    publication_status: Mapped[str] = mapped_column(String(32), default="blocked")
    metadata_json: Mapped[dict | None] = mapped_column(JSON)
    processing_run_id: Mapped[str | None] = mapped_column(ForeignKey("processing_runs.id"))


class Project(Base, TimestampMixin):
    __tablename__ = "projects"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(500))
    geography_id: Mapped[str | None] = mapped_column(ForeignKey("geographies.id"))
    project_status: Mapped[str] = mapped_column(String(32), default="synthetic")
    description: Mapped[str | None] = mapped_column(Text)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True)


class ValidationEvent(Base):
    __tablename__ = "validation_events"
    id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=lambda: str(uuid4())
    )
    entity_type: Mapped[str] = mapped_column(String(64))
    entity_id: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32))
    message: Mapped[str | None] = mapped_column(Text)
    checks_json: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


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
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class FinanceScenarioRecord(Base):
    """Immutable canonical finance scenario version."""

    __tablename__ = "finance_scenarios"
    __table_args__ = (
        UniqueConstraint(
            "scenario_id",
            "scenario_version",
            name="uq_finance_scenario_version",
        ),
        UniqueConstraint("input_hash", name="uq_finance_scenario_input_hash"),
        CheckConstraint(
            "monetary_basis IN ('real', 'nominal')",
            name="ck_finance_scenario_monetary_basis",
        ),
    )

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    scenario_id: Mapped[str] = mapped_column(String(128), nullable=False)
    scenario_version: Mapped[str] = mapped_column(String(128), nullable=False)
    formula_version: Mapped[str] = mapped_column(String(64), nullable=False)
    canonicalization_version: Mapped[str] = mapped_column(String(64), nullable=False)
    input_hash: Mapped[str] = mapped_column(String(80), nullable=False)
    geography_id: Mapped[str] = mapped_column(ForeignKey("geographies.id"))
    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id"))
    is_synthetic: Mapped[bool] = mapped_column(Boolean, nullable=False)
    reporting_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    price_year: Mapped[int] = mapped_column(Integer, nullable=False)
    monetary_basis: Mapped[str] = mapped_column(String(16), nullable=False)
    validation_status: Mapped[str] = mapped_column(String(32), nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    canonical_payload: Mapped[str] = mapped_column(Text, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )


class FinanceCalculationExecution(Base):
    """Immutable audit event for one execution of a deterministic run identity."""

    __tablename__ = "finance_calculation_executions"
    __table_args__ = (
        CheckConstraint(
            "status IN ('succeeded', 'failed')",
            name="ck_finance_execution_status",
        ),
    )

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    scenario_record_id: Mapped[str] = mapped_column(
        ForeignKey("finance_scenarios.id"), nullable=False
    )
    calculation_run_id: Mapped[str] = mapped_column(
        String(128), nullable=False, index=True
    )
    formula_version: Mapped[str] = mapped_column(String(64), nullable=False)
    input_hash: Mapped[str] = mapped_column(String(80), nullable=False)
    canonicalization_version: Mapped[str] = mapped_column(String(64), nullable=False)
    software_version: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class FinanceIndicatorResultRecord(Base):
    """Immutable typed result payload produced by one execution event."""

    __tablename__ = "finance_indicator_results"
    __table_args__ = (
        UniqueConstraint(
            "execution_id",
            "indicator_name",
            name="uq_finance_execution_indicator",
        ),
    )

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    execution_id: Mapped[str] = mapped_column(
        ForeignKey("finance_calculation_executions.id"), nullable=False, index=True
    )
    indicator_name: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    value_json: Mapped[dict | None] = mapped_column(JSON)
    result_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    lineage_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )


class FinanceValidationEventRecord(Base):
    """Immutable finance-specific validation evidence."""

    __tablename__ = "finance_validation_events"
    __table_args__ = (
        CheckConstraint(
            "status IN ('passed', 'warning', 'failed')",
            name="ck_finance_validation_status",
        ),
    )

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    scenario_record_id: Mapped[str] = mapped_column(
        ForeignKey("finance_scenarios.id"), nullable=False, index=True
    )
    execution_id: Mapped[str | None] = mapped_column(
        ForeignKey("finance_calculation_executions.id"), index=True
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    checks_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )


def _reject_finance_mutation(_mapper, _connection, target) -> None:
    """Reject ORM updates and deletes for append-only finance records."""
    raise ValueError(f"{type(target).__name__} is immutable and append-only.")


for _immutable_model in (
    FinanceScenarioRecord,
    FinanceCalculationExecution,
    FinanceIndicatorResultRecord,
    FinanceValidationEventRecord,
):
    event.listen(_immutable_model, "before_update", _reject_finance_mutation)
    event.listen(_immutable_model, "before_delete", _reject_finance_mutation)
