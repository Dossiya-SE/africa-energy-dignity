"""Create the DATA-001 registry tables."""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260730_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def timestamp_columns():
    """Return standard registry timestamp columns."""
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    ]


def upgrade() -> None:
    """Create PostGIS support and the foundational registry tables."""
    if op.get_bind().dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.create_table(
        "institutions",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("institution_type", sa.String(64), nullable=False),
        sa.Column("country_code", sa.String(3)),
        sa.Column("website", sa.String(500)),
        sa.Column("notes", sa.Text()),
        *timestamp_columns(),
    )
    op.create_table(
        "geographies",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("level", sa.String(64), nullable=False),
        sa.Column(
            "parent_id", sa.String(64), sa.ForeignKey("geographies.id")
        ),
        sa.Column("iso_code", sa.String(16), unique=True),
        sa.Column("geometry_status", sa.String(32), nullable=False),
        *timestamp_columns(),
    )
    op.create_table(
        "sources",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column(
            "publisher_id", sa.String(64), sa.ForeignKey("institutions.id")
        ),
        sa.Column("source_url", sa.String(1000), nullable=False),
        sa.Column("access_date", sa.String(10), nullable=False),
        sa.Column("temporal_coverage", sa.String(255)),
        sa.Column("geographic_coverage", sa.String(255)),
        sa.Column("licence", sa.String(255)),
        sa.Column("attribution", sa.Text()),
        sa.Column("limitations", sa.Text()),
        sa.Column("evidence_class", sa.String(32), nullable=False),
        sa.Column("validation_status", sa.String(32), nullable=False),
        sa.Column("checksum", sa.String(128)),
        *timestamp_columns(),
    )
    op.create_table(
        "datasets",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column(
            "source_id", sa.String(64), sa.ForeignKey("sources.id"), nullable=False
        ),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("version", sa.String(128)),
        sa.Column("variable_definition", sa.Text()),
        sa.Column("unit", sa.String(128)),
        *timestamp_columns(),
    )
    op.create_table(
        "geospatial_assets",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("dataset_id", sa.String(64), sa.ForeignKey("datasets.id")),
        sa.Column(
            "geography_id", sa.String(64), sa.ForeignKey("geographies.id")
        ),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("asset_type", sa.String(64), nullable=False),
        sa.Column("uri", sa.String(1000), nullable=False),
        sa.Column("spatial_resolution", sa.String(255)),
        sa.Column("temporal_coverage", sa.String(255)),
        sa.Column("licence", sa.String(255)),
        sa.Column("validation_status", sa.String(32), nullable=False),
        sa.Column("is_sensitive", sa.Boolean(), nullable=False),
        *timestamp_columns(),
    )
    op.create_table(
        "projects",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column(
            "geography_id", sa.String(64), sa.ForeignKey("geographies.id")
        ),
        sa.Column("project_status", sa.String(32), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("is_synthetic", sa.Boolean(), nullable=False),
        *timestamp_columns(),
    )
    op.create_table(
        "processing_runs",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("process_name", sa.String(255), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("code_commit", sa.String(64)),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "validation_events",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("entity_id", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("message", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "audit_events",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("actor", sa.String(255), nullable=False),
        sa.Column("action", sa.String(128), nullable=False),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("entity_id", sa.String(64), nullable=False),
        sa.Column("event_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    """Drop the registry in reverse dependency order."""
    for table in (
        "audit_events",
        "validation_events",
        "processing_runs",
        "projects",
        "geospatial_assets",
        "datasets",
        "sources",
        "geographies",
        "institutions",
    ):
        op.drop_table(table)
