"""Add immutable FIN-001 scenario, execution, result and validation records."""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260731_0005"
down_revision: Union[str, None] = "20260730_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "finance_scenarios",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column("scenario_id", sa.String(128), nullable=False),
        sa.Column("scenario_version", sa.String(128), nullable=False),
        sa.Column("formula_version", sa.String(64), nullable=False),
        sa.Column("canonicalization_version", sa.String(64), nullable=False),
        sa.Column("input_hash", sa.String(80), nullable=False),
        sa.Column(
            "geography_id",
            sa.String(64),
            sa.ForeignKey("geographies.id"),
            nullable=False,
        ),
        sa.Column(
            "project_id",
            sa.String(64),
            sa.ForeignKey("projects.id"),
        ),
        sa.Column("is_synthetic", sa.Boolean(), nullable=False),
        sa.Column("reporting_currency", sa.String(3), nullable=False),
        sa.Column("price_year", sa.Integer(), nullable=False),
        sa.Column("monetary_basis", sa.String(16), nullable=False),
        sa.Column("validation_status", sa.String(32), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("canonical_payload", sa.Text(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "scenario_id",
            "scenario_version",
            name="uq_finance_scenario_version",
        ),
        sa.UniqueConstraint("input_hash", name="uq_finance_scenario_input_hash"),
        sa.CheckConstraint(
            "monetary_basis IN ('real', 'nominal')",
            name="ck_finance_scenario_monetary_basis",
        ),
    )

    op.create_table(
        "finance_calculation_executions",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column(
            "scenario_record_id",
            sa.String(128),
            sa.ForeignKey("finance_scenarios.id"),
            nullable=False,
        ),
        sa.Column("calculation_run_id", sa.String(128), nullable=False),
        sa.Column("formula_version", sa.String(64), nullable=False),
        sa.Column("input_hash", sa.String(80), nullable=False),
        sa.Column("canonicalization_version", sa.String(64), nullable=False),
        sa.Column("software_version", sa.String(128), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("error_message", sa.Text()),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('succeeded', 'failed')",
            name="ck_finance_execution_status",
        ),
    )
    op.create_index(
        "ix_finance_calculation_executions_calculation_run_id",
        "finance_calculation_executions",
        ["calculation_run_id"],
    )

    op.create_table(
        "finance_indicator_results",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column(
            "execution_id",
            sa.String(128),
            sa.ForeignKey("finance_calculation_executions.id"),
            nullable=False,
        ),
        sa.Column("indicator_name", sa.String(128), nullable=False),
        sa.Column("status", sa.String(64), nullable=False),
        sa.Column("value_json", sa.JSON()),
        sa.Column("result_json", sa.JSON(), nullable=False),
        sa.Column("lineage_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "execution_id",
            "indicator_name",
            name="uq_finance_execution_indicator",
        ),
    )
    op.create_index(
        "ix_finance_indicator_results_execution_id",
        "finance_indicator_results",
        ["execution_id"],
    )

    op.create_table(
        "finance_validation_events",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column(
            "scenario_record_id",
            sa.String(128),
            sa.ForeignKey("finance_scenarios.id"),
            nullable=False,
        ),
        sa.Column(
            "execution_id",
            sa.String(128),
            sa.ForeignKey("finance_calculation_executions.id"),
        ),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("checks_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('passed', 'warning', 'failed')",
            name="ck_finance_validation_status",
        ),
    )
    op.create_index(
        "ix_finance_validation_events_scenario_record_id",
        "finance_validation_events",
        ["scenario_record_id"],
    )
    op.create_index(
        "ix_finance_validation_events_execution_id",
        "finance_validation_events",
        ["execution_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_finance_validation_events_execution_id",
        table_name="finance_validation_events",
    )
    op.drop_index(
        "ix_finance_validation_events_scenario_record_id",
        table_name="finance_validation_events",
    )
    op.drop_table("finance_validation_events")

    op.drop_index(
        "ix_finance_indicator_results_execution_id",
        table_name="finance_indicator_results",
    )
    op.drop_table("finance_indicator_results")

    op.drop_index(
        "ix_finance_calculation_executions_calculation_run_id",
        table_name="finance_calculation_executions",
    )
    op.drop_table("finance_calculation_executions")
    op.drop_table("finance_scenarios")
