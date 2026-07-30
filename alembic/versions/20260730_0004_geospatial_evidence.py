"""Add controlled geospatial provenance and publication fields."""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260730_0004"
down_revision: Union[str, None] = "20260730_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("datasets") as batch:
        batch.add_column(sa.Column("original_uri", sa.String(1000)))
        batch.add_column(sa.Column("checksum", sa.String(128)))
        batch.add_column(sa.Column("media_type", sa.String(128)))
        batch.add_column(sa.Column("metadata_json", sa.JSON()))
        batch.add_column(
            sa.Column(
                "validation_status",
                sa.String(32),
                nullable=False,
                server_default="proposed",
            )
        )
    with op.batch_alter_table("processing_runs") as batch:
        batch.add_column(sa.Column("input_checksum", sa.String(128)))
        batch.add_column(sa.Column("output_checksum", sa.String(128)))
        batch.add_column(sa.Column("parameters_json", sa.JSON()))
    with op.batch_alter_table("validation_events") as batch:
        batch.add_column(sa.Column("checks_json", sa.JSON()))
    with op.batch_alter_table("geospatial_assets") as batch:
        batch.add_column(sa.Column("checksum", sa.String(128)))
        batch.add_column(sa.Column("crs", sa.String(128)))
        batch.add_column(sa.Column("bbox_json", sa.JSON()))
        batch.add_column(sa.Column("nodata_json", sa.JSON()))
        batch.add_column(
            sa.Column(
                "publication_status",
                sa.String(32),
                nullable=False,
                server_default="blocked",
            )
        )
        batch.add_column(sa.Column("metadata_json", sa.JSON()))
        batch.add_column(sa.Column("processing_run_id", sa.String(64)))
        batch.create_foreign_key(
            "fk_geospatial_assets_processing_run",
            "processing_runs",
            ["processing_run_id"],
            ["id"],
        )
        batch.create_check_constraint(
            "ck_geospatial_publication_status",
            "publication_status IN ('blocked', 'published')",
        )


def downgrade() -> None:
    with op.batch_alter_table("geospatial_assets") as batch:
        batch.drop_constraint(
            "fk_geospatial_assets_processing_run",
            type_="foreignkey",
        )
        batch.drop_constraint("ck_geospatial_publication_status", type_="check")
        for column in (
            "processing_run_id",
            "metadata_json",
            "publication_status",
            "nodata_json",
            "bbox_json",
            "crs",
            "checksum",
        ):
            batch.drop_column(column)
    with op.batch_alter_table("validation_events") as batch:
        batch.drop_column("checks_json")
    with op.batch_alter_table("processing_runs") as batch:
        for column in ("parameters_json", "output_checksum", "input_checksum"):
            batch.drop_column(column)
    with op.batch_alter_table("datasets") as batch:
        for column in (
            "validation_status",
            "metadata_json",
            "media_type",
            "checksum",
            "original_uri",
        ):
            batch.drop_column(column)
