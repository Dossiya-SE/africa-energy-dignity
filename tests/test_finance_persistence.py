"""Regression tests for append-only FIN-001 persistence and migration 0005."""
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
import pytest
from sqlalchemy import create_engine, func, inspect, select
from sqlalchemy.orm import Session

from aed.database.models import (
    Base,
    FinanceCalculationExecution,
    FinanceIndicatorResultRecord,
    FinanceScenarioRecord,
    FinanceValidationEventRecord,
    Geography,
)
from aed.finance.calculations import internal_rate_of_return
from aed.finance.lineage import (
    attach_indicator_lineage,
    build_calculation_run_identity,
    canonical_scenario_bytes,
    scenario_input_hash,
)
from aed.finance.models import (
    CostItem,
    EnergyYear,
    EvidenceReference,
    FinanceScenario,
    FinancingComponent,
    Money,
)
from aed.finance.persistence import (
    FinancePersistenceConflict,
    FinancePersistenceError,
    FinanceValidationInput,
    persist_finance_scenario,
    record_calculation_execution,
    record_finance_validation_event,
)

NOW = datetime(2026, 7, 31, 6, 0, tzinfo=timezone.utc)


def evidence() -> EvidenceReference:
    return EvidenceReference(
        evidence_class="scenario",
        validation_status="schema_valid",
        responsible_contributor="Synthetic AED reviewer",
        limitations=["Synthetic value used only for persistence verification."],
    )


def money(amount: str) -> Money:
    return Money(
        amount=Decimal(amount),
        currency="XOF",
        price_year=2026,
        basis="real",
    )


def scenario() -> FinanceScenario:
    return FinanceScenario(
        scenario_id="finance.scenario.synthetic.persistence.v1",
        name="Synthetic persistence fixture",
        scenario_version="1.0.0",
        formula_version="FIN-001.1",
        geography_id="geo.bfa",
        is_synthetic=True,
        reporting_currency="XOF",
        price_year=2026,
        monetary_basis="real",
        discount_rate=Decimal("0.08"),
        discount_rate_basis="real",
        funding_requirement=money("100"),
        project_start_year=2026,
        project_lifetime_years=2,
        construction_years=0,
        cost_items=[
            CostItem(
                cost_id="cost.synthetic.capex",
                category="capex",
                timing_year=0,
                value=money("100"),
                evidence=evidence(),
            )
        ],
        annual_energy=[
            EnergyYear(
                year=1,
                energy=Decimal("10"),
                unit="MWh",
                evidence=evidence(),
            ),
            EnergyYear(
                year=2,
                energy=Decimal("10"),
                unit="MWh",
                evidence=evidence(),
            ),
        ],
        financing_components=[
            FinancingComponent(
                component_id="finance.synthetic.equity",
                type="equity",
                amount=money("100"),
                evidence=evidence(),
            )
        ],
        customer_classes=[],
        validation_status="schema_valid",
        responsible_contributor="Synthetic AED reviewer",
        created_at=NOW,
        updated_at=NOW,
    )


@pytest.fixture
def finance_db(tmp_path: Path):
    database_path = tmp_path / "finance-persistence.db"
    engine = create_engine(f"sqlite+pysqlite:///{database_path}")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        db.add(
            Geography(
                id="geo.bfa",
                name="Burkina Faso",
                level="country",
                iso_code="BFA",
                geometry_status="validated",
            )
        )
        db.commit()
        yield db
    Base.metadata.drop_all(engine)
    engine.dispose()


def lined_irr(finance_scenario: FinanceScenario, software_version: str = "0.1.0"):
    identity = build_calculation_run_identity(
        finance_scenario,
        software_version=software_version,
    )
    result = internal_rate_of_return([Decimal("-100"), Decimal("110")])
    return identity, attach_indicator_lineage(
        result,
        identity,
        indicator_name="irr",
    )


def test_forward_migration_from_0004_creates_finance_tables(tmp_path, monkeypatch):
    database_path = tmp_path / "finance-forward-migration.db"
    database_url = f"sqlite+pysqlite:///{database_path}"
    monkeypatch.delenv("AED_DATABASE_URL", raising=False)
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", database_url)

    command.upgrade(config, "20260730_0004")
    engine = create_engine(database_url)
    assert "finance_scenarios" not in inspect(engine).get_table_names()
    engine.dispose()

    command.upgrade(config, "head")
    engine = create_engine(database_url)
    tables = set(inspect(engine).get_table_names())
    with engine.connect() as connection:
        revision = MigrationContext.configure(connection).get_current_revision()

    assert revision == "20260731_0005"
    assert {
        "finance_scenarios",
        "finance_calculation_executions",
        "finance_indicator_results",
        "finance_validation_events",
    }.issubset(tables)
    engine.dispose()


def test_scenario_persistence_is_idempotent_and_canonical(finance_db: Session):
    finance_scenario = scenario()
    first = persist_finance_scenario(finance_db, finance_scenario)
    second = persist_finance_scenario(finance_db, finance_scenario)

    assert first.id == second.id
    assert first.input_hash == scenario_input_hash(finance_scenario)
    assert first.canonical_payload.encode("utf-8") == canonical_scenario_bytes(
        finance_scenario
    )
    count = finance_db.scalar(select(func.count()).select_from(FinanceScenarioRecord))
    assert count == 1


def test_same_scenario_version_cannot_be_overwritten(finance_db: Session):
    original = scenario()
    persist_finance_scenario(finance_db, original)
    payload = original.model_dump(mode="python")
    payload["discount_rate"] = Decimal("0.09")
    changed = FinanceScenario.model_validate(payload)

    with pytest.raises(FinancePersistenceConflict, match="different canonical content"):
        persist_finance_scenario(finance_db, changed)


def test_execution_records_are_append_only_and_distinct(finance_db: Session):
    finance_scenario = scenario()
    identity, result = lined_irr(finance_scenario)
    event = FinanceValidationInput(
        status="passed",
        message="Deterministic finance inputs and lineage passed.",
        checks={"input_hash": True, "formula_version": True},
    )

    first = record_calculation_execution(
        finance_db,
        scenario=finance_scenario,
        identity=identity,
        results={"irr": result},
        validation_events=[event],
        started_at=NOW,
        completed_at=NOW,
    )
    second = record_calculation_execution(
        finance_db,
        scenario=finance_scenario,
        identity=identity,
        results={"irr": result},
        started_at=NOW,
        completed_at=NOW,
    )

    assert first.id != second.id
    assert first.calculation_run_id == second.calculation_run_id
    assert first.calculation_run_id == identity.calculation_run_id
    assert finance_db.scalar(
        select(func.count()).select_from(FinanceCalculationExecution)
    ) == 2
    assert finance_db.scalar(
        select(func.count()).select_from(FinanceIndicatorResultRecord)
    ) == 2
    assert finance_db.scalar(
        select(func.count()).select_from(FinanceValidationEventRecord)
    ) == 1

    stored = finance_db.scalar(
        select(FinanceIndicatorResultRecord).where(
            FinanceIndicatorResultRecord.execution_id == first.id
        )
    )
    assert stored is not None
    assert stored.status == "unique_root"
    assert stored.lineage_json["input_hash"] == identity.input_hash
    assert stored.result_json["formula_version"] == "FIN-001.1"


def test_result_without_matching_lineage_is_rejected(finance_db: Session):
    finance_scenario = scenario()
    identity = build_calculation_run_identity(
        finance_scenario,
        software_version="0.1.0",
    )
    result = internal_rate_of_return([Decimal("-100"), Decimal("110")])

    with pytest.raises(
        FinancePersistenceError,
        match="must carry deterministic lineage",
    ):
        record_calculation_execution(
            finance_db,
            scenario=finance_scenario,
            identity=identity,
            results={"irr": result},
        )


def test_identity_must_match_canonical_scenario(finance_db: Session):
    finance_scenario = scenario()
    other_payload = finance_scenario.model_dump(mode="python")
    other_payload["scenario_version"] = "1.0.1"
    other = FinanceScenario.model_validate(other_payload)
    wrong_identity = build_calculation_run_identity(other, software_version="0.1.0")
    _, result = lined_irr(finance_scenario)

    with pytest.raises(FinancePersistenceError, match="does not match"):
        record_calculation_execution(
            finance_db,
            scenario=finance_scenario,
            identity=wrong_identity,
            results={"irr": result},
        )


def test_failed_execution_requires_error_message(finance_db: Session):
    finance_scenario = scenario()
    identity = build_calculation_run_identity(
        finance_scenario,
        software_version="0.1.0",
    )

    with pytest.raises(FinancePersistenceError, match="requires an error message"):
        record_calculation_execution(
            finance_db,
            scenario=finance_scenario,
            identity=identity,
            results={},
            status="failed",
        )


def test_validation_event_can_be_recorded_without_execution(finance_db: Session):
    finance_scenario = scenario()
    record = record_finance_validation_event(
        finance_db,
        scenario=finance_scenario,
        event_input=FinanceValidationInput(
            status="warning",
            message="Synthetic fixture remains unsuitable for real-project claims.",
            checks={"is_synthetic": True},
        ),
    )

    assert record.execution_id is None
    assert record.status == "warning"
    assert record.checks_json == {"is_synthetic": True}


def test_finance_records_reject_update_and_delete(finance_db: Session):
    record = persist_finance_scenario(finance_db, scenario())
    record.validation_status = "validated"
    with pytest.raises(ValueError, match="immutable and append-only"):
        finance_db.commit()
    finance_db.rollback()

    stored = finance_db.get(FinanceScenarioRecord, record.id)
    assert stored is not None
    finance_db.delete(stored)
    with pytest.raises(ValueError, match="immutable and append-only"):
        finance_db.commit()
    finance_db.rollback()


def test_execution_timestamps_must_be_ordered_and_timezone_aware(finance_db: Session):
    finance_scenario = scenario()
    identity, result = lined_irr(finance_scenario)
    naive = datetime(2026, 7, 31, 6, 0)

    with pytest.raises(FinancePersistenceError, match="timezone-aware"):
        record_calculation_execution(
            finance_db,
            scenario=finance_scenario,
            identity=identity,
            results={"irr": result},
            started_at=naive,
            completed_at=NOW,
        )
