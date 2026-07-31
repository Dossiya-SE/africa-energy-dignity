"""Regression tests for the controlled synthetic FIN-001 seed path."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from aed.database.models import (
    Base,
    FinanceCalculationExecution,
    FinanceIndicatorResultRecord,
    FinanceScenarioRecord,
    FinanceValidationEventRecord,
)
from aed.finance import (
    FinancePersistenceConflict,
    build_calculation_run_identity,
    scenario_input_hash,
)
from scripts.seed_finance import (
    DEFAULT_FIXTURE,
    EXPECTED_INDICATORS,
    SEED_SOFTWARE_VERSION,
    load_synthetic_scenario,
    seed_synthetic_finance,
    validate_synthetic_fixture,
)


@pytest.fixture
def finance_database_url(tmp_path: Path) -> str:
    database_path = tmp_path / "finance-seed.db"
    database_url = f"sqlite+pysqlite:///{database_path}"
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    engine.dispose()
    return database_url


def _write_modified_fixture(
    tmp_path: Path,
    *,
    discount_rate: str | None = None,
    scenario_version: str | None = None,
) -> Path:
    payload = json.loads(DEFAULT_FIXTURE.read_text(encoding="utf-8"))
    if discount_rate is not None:
        payload["discount_rate"] = discount_rate
    if scenario_version is not None:
        payload["scenario_version"] = scenario_version
    path = tmp_path / "modified-finance-fixture.json"
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def test_fixture_is_explicitly_synthetic_and_deterministic():
    first = load_synthetic_scenario()
    second = load_synthetic_scenario()

    assert first.is_synthetic is True
    assert "synthetic" in first.name.casefold()
    assert first.project_id is None
    assert first.geography_id == "geo.bfa"
    assert scenario_input_hash(first) == scenario_input_hash(second)
    assert (
        build_calculation_run_identity(
            first,
            software_version=SEED_SOFTWARE_VERSION,
        )
        == build_calculation_run_identity(
            second,
            software_version=SEED_SOFTWARE_VERSION,
        )
    )

    evidence_records = [
        *(item.evidence for item in first.cost_items),
        *(item.evidence for item in first.annual_energy),
        *(item.evidence for item in first.financing_components),
        *(item.evidence for item in first.customer_classes),
    ]
    assert evidence_records
    assert all(
        item.evidence_class in {"scenario", "assumed"}
        for item in evidence_records
    )
    assert all(item.source_id is None for item in evidence_records)
    assert all(item.limitations for item in evidence_records)


def test_seed_is_idempotent(finance_database_url: str):
    first = seed_synthetic_finance(database_url=finance_database_url)
    second = seed_synthetic_finance(database_url=finance_database_url)

    assert first.created_execution is True
    assert second.created_execution is False
    assert first.scenario_record_id == second.scenario_record_id
    assert first.scenario_input_hash == second.scenario_input_hash
    assert first.calculation_run_id == second.calculation_run_id
    assert first.execution_id == second.execution_id

    engine = create_engine(finance_database_url)
    with Session(engine) as db:
        assert db.scalar(
            select(func.count()).select_from(FinanceScenarioRecord)
        ) == 1
        assert db.scalar(
            select(func.count()).select_from(FinanceCalculationExecution)
        ) == 1
        assert db.scalar(
            select(func.count()).select_from(FinanceIndicatorResultRecord)
        ) == len(EXPECTED_INDICATORS)
        assert db.scalar(
            select(func.count()).select_from(FinanceValidationEventRecord)
        ) == 1
        stored_names = set(
            db.scalars(
                select(FinanceIndicatorResultRecord.indicator_name)
            )
        )
        assert stored_names == set(EXPECTED_INDICATORS)
    engine.dispose()


def test_changed_content_with_same_version_is_rejected(
    finance_database_url: str,
    tmp_path: Path,
):
    seed_synthetic_finance(database_url=finance_database_url)
    changed = _write_modified_fixture(
        tmp_path,
        discount_rate="0.09",
    )

    with pytest.raises(
        FinancePersistenceConflict,
        match="different canonical content",
    ):
        seed_synthetic_finance(
            database_url=finance_database_url,
            fixture_path=changed,
        )


def test_changed_content_with_new_version_is_distinct(
    finance_database_url: str,
    tmp_path: Path,
):
    first = seed_synthetic_finance(database_url=finance_database_url)
    changed = _write_modified_fixture(
        tmp_path,
        discount_rate="0.09",
        scenario_version="1.0.1",
    )
    second = seed_synthetic_finance(
        database_url=finance_database_url,
        fixture_path=changed,
    )

    assert first.scenario_record_id != second.scenario_record_id
    assert first.scenario_input_hash != second.scenario_input_hash
    assert first.calculation_run_id != second.calculation_run_id
    assert second.created_execution is True

    engine = create_engine(finance_database_url)
    with Session(engine) as db:
        assert db.scalar(
            select(func.count()).select_from(FinanceScenarioRecord)
        ) == 2
        assert db.scalar(
            select(func.count()).select_from(FinanceCalculationExecution)
        ) == 2
        assert db.scalar(
            select(func.count()).select_from(FinanceIndicatorResultRecord)
        ) == 2 * len(EXPECTED_INDICATORS)
    engine.dispose()


def test_validation_rejects_non_synthetic_claim():
    scenario = load_synthetic_scenario()
    payload = scenario.model_dump(mode="python")
    payload["is_synthetic"] = False
    payload["project_id"] = "project.claimed.real"
    altered = type(scenario).model_validate(payload)

    with pytest.raises(
        ValueError,
        match="controlled fixture must be synthetic",
    ):
        validate_synthetic_fixture(altered)
