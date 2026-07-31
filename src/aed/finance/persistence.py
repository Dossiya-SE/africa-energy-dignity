"""Append-only persistence for FIN-001 scenarios, executions and results."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from aed.database.models import (
    FinanceCalculationExecution,
    FinanceIndicatorResultRecord,
    FinanceScenarioRecord,
    FinanceValidationEventRecord,
)
from aed.finance.lineage import (
    build_calculation_run_identity,
    build_indicator_lineage,
    canonical_scenario_bytes,
    scenario_input_hash,
)
from aed.finance.models import (
    CalculationRunIdentity,
    DeterministicIndicatorResult,
    FinanceScenario,
)

ExecutionStatus = Literal["succeeded", "failed"]
ValidationStatus = Literal["passed", "warning", "failed"]


class FinancePersistenceError(ValueError):
    """Base error for invalid or conflicting persistence operations."""


class FinancePersistenceConflict(FinancePersistenceError):
    """Raised when an immutable identity already exists with different content."""


@dataclass(frozen=True)
class FinanceValidationInput:
    """Validated input for one append-only finance validation event."""

    status: ValidationStatus
    message: str
    checks: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.status not in {"passed", "warning", "failed"}:
            raise FinancePersistenceError("Unsupported finance validation status.")
        if not self.message.strip():
            raise FinancePersistenceError(
                "Finance validation message must be non-empty."
            )


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _require_aware_timestamp(value: datetime, label: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise FinancePersistenceError(f"{label} must be timezone-aware.")


def _scenario_record_id(input_hash: str) -> str:
    return f"finance.scenario.{input_hash.replace(':', '.')}"


def _new_id(prefix: str) -> str:
    return f"{prefix}.{uuid4()}"


def _ensure_scenario_record(
    db: Session,
    scenario: FinanceScenario,
) -> FinanceScenarioRecord:
    input_hash = scenario_input_hash(scenario)
    canonical_payload = canonical_scenario_bytes(scenario).decode("utf-8")

    existing_version = db.scalar(
        select(FinanceScenarioRecord).where(
            FinanceScenarioRecord.scenario_id == scenario.scenario_id,
            FinanceScenarioRecord.scenario_version == scenario.scenario_version,
        )
    )
    if existing_version is not None:
        if (
            existing_version.input_hash != input_hash
            or existing_version.canonical_payload != canonical_payload
        ):
            raise FinancePersistenceConflict(
                "Scenario ID and version already exist with different canonical content."
            )
        return existing_version

    existing_hash = db.scalar(
        select(FinanceScenarioRecord).where(
            FinanceScenarioRecord.input_hash == input_hash
        )
    )
    if existing_hash is not None:
        if (
            existing_hash.scenario_id != scenario.scenario_id
            or existing_hash.scenario_version != scenario.scenario_version
        ):
            raise FinancePersistenceConflict(
                "Scenario input hash is already bound to another scenario identity."
            )
        return existing_hash

    record = FinanceScenarioRecord(
        id=_scenario_record_id(input_hash),
        scenario_id=scenario.scenario_id,
        scenario_version=scenario.scenario_version,
        formula_version=scenario.formula_version,
        canonicalization_version="FIN-CANONICAL-JSON-1",
        input_hash=input_hash,
        geography_id=scenario.geography_id,
        project_id=scenario.project_id,
        is_synthetic=scenario.is_synthetic,
        reporting_currency=scenario.reporting_currency,
        price_year=scenario.price_year,
        monetary_basis=scenario.monetary_basis,
        validation_status=scenario.validation_status,
        payload_json=scenario.model_dump(
            mode="json",
            by_alias=True,
            exclude_none=False,
        ),
        canonical_payload=canonical_payload,
    )
    db.add(record)
    db.flush()
    return record


def persist_finance_scenario(
    db: Session,
    scenario: FinanceScenario,
) -> FinanceScenarioRecord:
    """Persist one immutable scenario version, idempotently by canonical identity."""
    try:
        record = _ensure_scenario_record(db, scenario)
        db.commit()
        db.refresh(record)
        return record
    except IntegrityError as error:
        db.rollback()
        raise FinancePersistenceConflict(
            "Finance scenario conflicts with an existing immutable record."
        ) from error
    except Exception:
        db.rollback()
        raise


def _validate_identity(
    scenario: FinanceScenario,
    identity: CalculationRunIdentity,
) -> None:
    expected = build_calculation_run_identity(
        scenario,
        software_version=identity.software_version,
    )
    if expected.model_dump() != identity.model_dump():
        raise FinancePersistenceError(
            "Calculation-run identity does not match the canonical scenario."
        )


def _validate_result_lineage(
    indicator_name: str,
    result: DeterministicIndicatorResult,
    identity: CalculationRunIdentity,
) -> None:
    if result.lineage is None:
        raise FinancePersistenceError(
            f"Indicator {indicator_name} must carry deterministic lineage."
        )
    expected = build_indicator_lineage(
        identity,
        indicator_name=indicator_name,
    )
    if result.lineage.model_dump() != expected.model_dump():
        raise FinancePersistenceError(
            f"Indicator {indicator_name} lineage does not match the execution identity."
        )


def record_calculation_execution(
    db: Session,
    *,
    scenario: FinanceScenario,
    identity: CalculationRunIdentity,
    results: Mapping[str, DeterministicIndicatorResult],
    validation_events: Sequence[FinanceValidationInput] = (),
    status: ExecutionStatus = "succeeded",
    error_message: str | None = None,
    started_at: datetime | None = None,
    completed_at: datetime | None = None,
) -> FinanceCalculationExecution:
    """Atomically append one execution, its typed results and validation events."""
    if status not in {"succeeded", "failed"}:
        raise FinancePersistenceError("Unsupported finance execution status.")
    if status == "succeeded" and not results:
        raise FinancePersistenceError(
            "A successful calculation execution requires at least one result."
        )
    if status == "failed" and not error_message:
        raise FinancePersistenceError("A failed execution requires an error message.")

    _validate_identity(scenario, identity)
    for indicator_name, result in results.items():
        if not indicator_name.strip():
            raise FinancePersistenceError("Indicator names must be non-empty.")
        _validate_result_lineage(indicator_name, result, identity)

    started = started_at or _utcnow()
    completed = completed_at or _utcnow()
    _require_aware_timestamp(started, "started_at")
    _require_aware_timestamp(completed, "completed_at")
    if completed < started:
        raise FinancePersistenceError("completed_at cannot precede started_at.")

    try:
        scenario_record = _ensure_scenario_record(db, scenario)
        execution = FinanceCalculationExecution(
            id=_new_id("finance.execution"),
            scenario_record_id=scenario_record.id,
            calculation_run_id=identity.calculation_run_id,
            formula_version=identity.formula_version,
            input_hash=identity.input_hash,
            canonicalization_version=identity.canonicalization_version,
            software_version=identity.software_version,
            status=status,
            error_message=error_message,
            started_at=started,
            completed_at=completed,
        )
        db.add(execution)
        db.flush()

        for indicator_name, result in results.items():
            result_payload = result.model_dump(mode="json", exclude_none=False)
            lineage_payload = result.lineage.model_dump(mode="json")
            value_payload = {
                key: result_payload[key]
                for key in (
                    "value",
                    "initial_llcr",
                    "minimum_llcr",
                    "period_values",
                )
                if key in result_payload
            }
            db.add(
                FinanceIndicatorResultRecord(
                    id=_new_id("finance.result"),
                    execution_id=execution.id,
                    indicator_name=indicator_name,
                    status=str(result_payload.get("status", "calculated")),
                    value_json=value_payload or None,
                    result_json=result_payload,
                    lineage_json=lineage_payload,
                )
            )

        for event_input in validation_events:
            db.add(
                FinanceValidationEventRecord(
                    id=_new_id("finance.validation"),
                    scenario_record_id=scenario_record.id,
                    execution_id=execution.id,
                    status=event_input.status,
                    message=event_input.message,
                    checks_json=event_input.checks,
                )
            )

        db.commit()
        db.refresh(execution)
        return execution
    except IntegrityError as error:
        db.rollback()
        raise FinancePersistenceConflict(
            "Finance execution conflicts with an existing immutable record."
        ) from error
    except Exception:
        db.rollback()
        raise


def record_finance_validation_event(
    db: Session,
    *,
    scenario: FinanceScenario,
    event_input: FinanceValidationInput,
    execution_id: str | None = None,
) -> FinanceValidationEventRecord:
    """Append one finance validation event independently of calculation results."""
    try:
        scenario_record = _ensure_scenario_record(db, scenario)
        if execution_id is not None:
            execution = db.get(FinanceCalculationExecution, execution_id)
            if execution is None or execution.scenario_record_id != scenario_record.id:
                raise FinancePersistenceError(
                    "Validation execution must belong to the same scenario record."
                )
        record = FinanceValidationEventRecord(
            id=_new_id("finance.validation"),
            scenario_record_id=scenario_record.id,
            execution_id=execution_id,
            status=event_input.status,
            message=event_input.message,
            checks_json=event_input.checks,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    except IntegrityError as error:
        db.rollback()
        raise FinancePersistenceConflict(
            "Finance validation event conflicts with an immutable record."
        ) from error
    except Exception:
        db.rollback()
        raise
