"""Relax obsolete DATA-001 source columns after canonical migration."""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260730_0003"
down_revision: Union[str, None] = "20260730_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Allow canonical writes without duplicating obsolete compatibility fields."""
    with op.batch_alter_table("sources") as batch:
        batch.alter_column(
            "access_date",
            existing_type=sa.String(10),
            nullable=True,
        )
        batch.alter_column(
            "validation_status",
            existing_type=sa.String(32),
            nullable=True,
        )


def downgrade() -> None:
    """Reconstruct legacy values before restoring their non-null constraints."""
    bind = op.get_bind()
    sources = sa.Table("sources", sa.MetaData(), autoload_with=bind)
    rows = bind.execute(sa.select(sources)).mappings().all()

    legacy_state = {
        "schema_valid": "reviewed",
        "validated": "validated",
        "rejected": "rejected",
    }

    for row in rows:
        access_date_value = row["access_date_value"]
        bind.execute(
            sources.update()
            .where(sources.c.id == row["id"])
            .values(
                access_date=(
                    access_date_value.isoformat()
                    if access_date_value is not None
                    else "1970-01-01"
                ),
                validation_status=legacy_state.get(
                    row["verification_status"], "proposed"
                ),
            )
        )

    with op.batch_alter_table("sources") as batch:
        batch.alter_column(
            "access_date",
            existing_type=sa.String(10),
            nullable=False,
        )
        batch.alter_column(
            "validation_status",
            existing_type=sa.String(32),
            nullable=False,
        )
