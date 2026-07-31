"""Seed one controlled, visibly synthetic FIN-001 finance scenario."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from aed.database.models import (
    FinanceCalculationExecution,
    FinanceIndicatorResultRecord,
    Geography,
)
from aed.database.session import build_engine
from aed.finance import (
    FinancePersistenceConflict,
    FinancePersistenceError,
    FinanceScenario,
    FinanceValidationInput,
    attach_indicator_lineage,
    build_calculation_run_identity,
    discounted_payback,
    internal_rate_of_return,
    lifecycle_cash_flows,
    persist_finance_scenario,
    record_calculation_execution,
    simple_payback,
)
from aed.finance.models import EvidenceReference

DEFAULT_FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "fixtures"
    / "finance"
    / "bfa_synthetic_energy_project.json"
)
SEED_SOFTWARE_VERSION = "AED-FIN-001-SYNTHETIC-SEED-1"
EXPECTED_INDICATORS = (
    "irr",
    "simple_payback",
    "discounted_payback",
)


@dataclass(frozen=True)
class FinanceSeedSummary:
    """Stable identifiers returned by one seed operation."""

    scenario_record_id: str
    scenario_input_hash: str
    calculation_run_id: str
    execution_id: str
    created_execution: bool


def _iter_evidence(scenario: FinanceScenario) -> Iterable[EvidenceReference]:
    for item in scenario.cost_items:
        yield item.evidence
    for item in scenario.annual_energy:
        yield item.evidence
    for item in scenario.financing_components:
        yield item.evidence
    for item in scenario.customer_classes:
        yield item.evidence


def validate_synthetic_fixture(scenario: FinanceScenario) -> None:
    """Reject fixture content that could be mistaken for verified project data."""
    if not scenario.is_synthetic:
        raise FinancePersistenceError("The controlled fixture must be synthetic.")
    if "synthetic" not in scenario.name.casefold():
        raise FinancePersistenceError(
            "The controlled fixture name must explicitly contain 'Synthetic'."
        )
    if scenario.project_id is not None:
        raise FinancePersistenceError(
            "The controlled fixture must not reference a real project record."
        )

    evidence_records = list(_iter_evidence(scenario))
    if not evidence_records:
        raise FinancePersistenceError(
            "The controlled fixture requires explicit evidence records."
        )
    for evidence in evidence_records:
        if evidence.evidence_class not in {"scenario", "assumed"}:
            raise FinancePersistenceError(
                "Synthetic fixture evidence must be classified as scenario or assumed."
            )
        if evidence.source_id is not None:
            raise FinancePersistenceError(
                "Synthetic fixture assumptions must not claim published source records."
            )
        if not evidence.limitations or any(
            not limitation.strip() for limitation in evidence.limitations
        ):
            raise FinancePersistenceError(
                "Every synthetic assumption requires a non-empty limitation."
            )


def load_synthetic_scenario(
    fixture_path: Path = DEFAULT_FIXTURE,
) -> FinanceScenario:
    """Load and validate the controlled JSON fixture."""
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    scenario = FinanceScenario.model_validate(payload)
    validate_synthetic_fixture(scenario)
    return scenario


def _ensure_burkina_geography(db: Session, geography_id: str) -> Geography:
    if geography_id != "geo.bfa":
        raise FinancePersistenceError(
            "The controlled Burkina Faso fixture must use geography_id geo.bfa."
        )
    existing = db.get(Geography, geography_id)
    if existing is not None:
        if existing.iso_code != "BFA" or existing.level != "country":
            raise FinancePersistenceConflict(
                "geo.bfa exists with incompatible geography metadata."
            )
        return existing

    geography = Geography(
        id="geo.bfa",
        name="Burkina Faso",
        level="country",
        iso_code="BFA",
        geometry_status="validated",
    )
    db.add(geography)
    db.commit()
    db.refresh(geography)
    return geography


def _build_seed_results(scenario: FinanceScenario):
    identity = build_calculation_run_identity(
        scenario,
        software_version=SEED_SOFTWARE_VERSION,
    )
    cash_flow_map = lifecycle_cash_flows(scenario)
    cash_flows = [
        cash_flow_map[year]
        for year in range(scenario.project_lifetime_years + 1)
    ]
    raw_results = {
        "irr": internal_rate_of_return(cash_flows),
        "simple_payback": simple_payback(cash_flows),
        "discounted_payback": discounted_payback(
            cash_flows,
            scenario.discount_rate,
            cash_flow_basis=scenario.monetary_basis,
            discount_rate_basis=scenario.discount_rate_basis,
        ),
    }
    results = {
        name: attach_indicator_lineage(
            result,
            identity,
            indicator_name=name,
        )
        for name, result in raw_results.items()
    }
    return identity, results


def _find_existing_execution(
    db: Session,
    *,
    scenario_record_id: str,
    calculation_run_id: str,
) -> FinanceCalculationExecution | None:
    executions = list(
        db.scalars(
            select(FinanceCalculationExecution)
            .where(
                FinanceCalculationExecution.scenario_record_id
                == scenario_record_id,
                FinanceCalculationExecution.calculation_run_id
                == calculation_run_id,
                FinanceCalculationExecution.status == "succeeded",
            )
            .order_by(FinanceCalculationExecution.started_at)
        )
    )
    if len(executions) > 1:
        raise FinancePersistenceConflict(
            "More than one successful seed execution exists for the run identity."
        )
    return executions[0] if executions else None


def _verify_existing_results(
    db: Session,
    execution: FinanceCalculationExecution,
) -> None:
    names = set(
        db.scalars(
            select(FinanceIndicatorResultRecord.indicator_name).where(
                FinanceIndicatorResultRecord.execution_id == execution.id
            )
        )
    )
    if names != set(EXPECTED_INDICATORS):
        raise FinancePersistenceConflict(
            "Existing seed execution has an incomplete or conflicting result set."
        )


def seed_synthetic_finance(
    *,
    database_url: str | None = None,
    fixture_path: Path = DEFAULT_FIXTURE,
) -> FinanceSeedSummary:
    """Persist the controlled scenario and one idempotent calculation execution."""
    scenario = load_synthetic_scenario(fixture_path)
    engine = build_engine(database_url)
    try:
        with Session(engine) as db:
            _ensure_burkina_geography(db, scenario.geography_id)

            scenario_record = persist_finance_scenario(db, scenario)
            identity, results = _build_seed_results(scenario)
            existing = _find_existing_execution(
                db,
                scenario_record_id=scenario_record.id,
                calculation_run_id=identity.calculation_run_id,
            )
            if existing is not None:
                _verify_existing_results(db, existing)
                return FinanceSeedSummary(
                    scenario_record_id=scenario_record.id,
                    scenario_input_hash=scenario_record.input_hash,
                    calculation_run_id=identity.calculation_run_id,
                    execution_id=existing.id,
                    created_execution=False,
                )

            execution = record_calculation_execution(
                db,
                scenario=scenario,
                identity=identity,
                results=results,
                validation_events=[
                    FinanceValidationInput(
                        status="warning",
                        message=(
                            "Synthetic FIN-001 fixture passed structural checks "
                            "and is prohibited from real-project claims."
                        ),
                        checks={
                            "is_synthetic": True,
                            "fixture_name_discloses_synthetic_status": True,
                            "evidence_classes_controlled": True,
                            "limitations_present": True,
                            "published_source_claims_absent": True,
                        },
                    )
                ],
                started_at=scenario.updated_at,
                completed_at=scenario.updated_at,
            )
            return FinanceSeedSummary(
                scenario_record_id=scenario_record.id,
                scenario_input_hash=scenario_record.input_hash,
                calculation_run_id=identity.calculation_run_id,
                execution_id=execution.id,
                created_execution=True,
            )
    finally:
        engine.dispose()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Seed the controlled synthetic FIN-001 finance fixture."
    )
    parser.add_argument(
        "--database-url",
        default=None,
        help="Override AED_DATABASE_URL for this seed execution.",
    )
    parser.add_argument(
        "--fixture",
        type=Path,
        default=DEFAULT_FIXTURE,
        help="Path to the controlled synthetic finance fixture.",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    summary = seed_synthetic_finance(
        database_url=args.database_url,
        fixture_path=args.fixture,
    )
    print(
        json.dumps(
            {
                "scenario_record_id": summary.scenario_record_id,
                "scenario_input_hash": summary.scenario_input_hash,
                "calculation_run_id": summary.calculation_run_id,
                "execution_id": summary.execution_id,
                "created_execution": summary.created_execution,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
