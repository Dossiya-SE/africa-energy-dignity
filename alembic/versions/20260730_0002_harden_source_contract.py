"""Harden canonical source metadata without rewriting migration history."""
from datetime import date
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260730_0002"
down_revision: Union[str, None] = "20260730_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _mapped_state(evidence_class: str, legacy_state: str) -> tuple[str, str]:
    evidence = "unverified" if evidence_class == "synthetic" else evidence_class
    mapping = {
        "reviewed": "schema_valid",
        "validated": "validated",
        "proposed": "proposed",
        "rejected": "rejected",
    }
    state = mapping.get(legacy_state, "proposed")
    if evidence == "unverified" and state in {
        "source_verified",
        "cross_checked",
        "model_ready",
        "validated",
    }:
        state = "proposed"
    return evidence, state


def upgrade() -> None:
    """Add typed canonical fields, transform existing rows and enforce invariants."""
    with op.batch_alter_table("sources") as batch:
        batch.alter_column(
            "source_url",
            existing_type=sa.String(1000),
            nullable=True,
        )
        batch.add_column(sa.Column("original_publisher", sa.String(500)))
        batch.add_column(sa.Column("persistent_identifier", sa.String(500)))
        batch.add_column(sa.Column("archive_reference", sa.String(500)))
        batch.add_column(sa.Column("access_date_value", sa.Date()))
        batch.add_column(sa.Column("temporal_coverage_json", sa.JSON()))
        batch.add_column(sa.Column("geographic_coverage_json", sa.JSON()))
        batch.add_column(sa.Column("attribution_requirements", sa.Text()))
        batch.add_column(sa.Column("access_method", sa.String(255)))
        batch.add_column(sa.Column("known_limitations_json", sa.JSON()))
        batch.add_column(sa.Column("verification_status", sa.String(32)))
        batch.add_column(sa.Column("responsible_reviewer", sa.String(255)))
        batch.add_column(sa.Column("source_version", sa.String(128)))

    bind = op.get_bind()
    metadata = sa.MetaData()
    sources = sa.Table("sources", metadata, autoload_with=bind)
    rows = bind.execute(sa.select(sources)).mappings().all()

    for row in rows:
        evidence, state = _mapped_state(
            row["evidence_class"], row["validation_status"]
        )
        temporal_description = (
            row["temporal_coverage"] or "Temporal coverage not yet verified."
        )
        geography = row["geographic_coverage"] or "unknown"
        limitation = row["limitations"] or "Known limitations pending verification."
        attribution = (
            row["attribution"] or "Attribution requirements pending verification."
        )
        licence = row["licence"] or "licence_unknown"
        publisher = (
            row["publisher_id"]
            or "Publisher pending original-source verification"
        )
        bind.execute(
            sources.update()
            .where(sources.c.id == row["id"])
            .values(
                original_publisher=publisher,
                access_date_value=date.fromisoformat(row["access_date"]),
                temporal_coverage_json={"description": temporal_description},
                geographic_coverage_json=[geography],
                licence=licence,
                attribution_requirements=attribution,
                access_method="Legacy DATA-001 registry record.",
                known_limitations_json=[limitation],
                evidence_class=evidence,
                verification_status=state,
                responsible_reviewer="Dossiya Dakou",
                source_version="0.1",
            )
        )

    with op.batch_alter_table("sources") as batch:
        batch.alter_column(
            "original_publisher", existing_type=sa.String(500), nullable=False
        )
        batch.alter_column(
            "access_date_value", existing_type=sa.Date(), nullable=False
        )
        batch.alter_column(
            "temporal_coverage_json", existing_type=sa.JSON(), nullable=False
        )
        batch.alter_column(
            "geographic_coverage_json", existing_type=sa.JSON(), nullable=False
        )
        batch.alter_column(
            "licence", existing_type=sa.String(255), nullable=False
        )
        batch.alter_column(
            "attribution_requirements", existing_type=sa.Text(), nullable=False
        )
        batch.alter_column(
            "access_method", existing_type=sa.String(255), nullable=False
        )
        batch.alter_column(
            "known_limitations_json", existing_type=sa.JSON(), nullable=False
        )
        batch.alter_column(
            "verification_status", existing_type=sa.String(32), nullable=False
        )
        batch.alter_column(
            "responsible_reviewer", existing_type=sa.String(255), nullable=False
        )
        batch.alter_column(
            "source_version", existing_type=sa.String(128), nullable=False
        )
        batch.create_check_constraint(
            "ck_sources_has_locator",
            "source_url IS NOT NULL OR persistent_identifier IS NOT NULL "
            "OR archive_reference IS NOT NULL",
        )


def downgrade() -> None:
    """Remove hardened columns while preserving legacy DATA-001 columns."""
    bind = op.get_bind()
    sources = sa.Table("sources", sa.MetaData(), autoload_with=bind)
    bind.execute(
        sources.update()
        .where(sources.c.source_url.is_(None))
        .values(source_url="https://example.invalid/legacy-source")
    )
    with op.batch_alter_table("sources") as batch:
        batch.drop_constraint("ck_sources_has_locator", type_="check")
        for column in (
            "source_version",
            "responsible_reviewer",
            "verification_status",
            "known_limitations_json",
            "access_method",
            "attribution_requirements",
            "geographic_coverage_json",
            "temporal_coverage_json",
            "access_date_value",
            "archive_reference",
            "persistent_identifier",
            "original_publisher",
        ):
            batch.drop_column(column)
        batch.alter_column(
            "source_url", existing_type=sa.String(1000), nullable=False
        )
