"""Transparent, append-only FIN-001 finance endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from aed.database.models import (
    FinanceCalculationExecution,
    FinanceIndicatorResultRecord,
    FinanceScenarioRecord,
    FinanceValidationEventRecord,
    Geography,
    Project,
)
from aed.database.session import get_db
from aed.finance.api_models import (
    FinanceAffordabilityPage,
    FinanceAffordabilityRead,
    FinanceCalculationRequest,
    FinanceCashFlowResponse,
    FinanceCashFlowYear,
    FinanceExecutionRead,
    FinanceIndicatorPage,
    FinanceIndicatorRead,
    FinanceScenarioDetail,
    FinanceScenarioPage,
    FinanceScenarioSummary,
    FinanceValidationPage,
    FinanceValidationRead,
)
from aed.finance.execution import (
    FinanceCalculationRejected,
    cash_flow_rows,
    execute_scenario_record,
    scenario_from_record,
)
from aed.finance.models import FinanceScenario
from aed.finance.persistence import (
    FinancePersistenceConflict,
    FinancePersistenceError,
    persist_finance_scenario,
)

router = APIRouter(prefix="/finance", tags=["finance"])
DEFAULT_LIMIT = 50
MAX_LIMIT = 100


def _scenario_summary(record: FinanceScenarioRecord) -> FinanceScenarioSummary:
    scenario = scenario_from_record(record)
    return FinanceScenarioSummary(
        scenario_record_id=record.id,
        scenario_id=record.scenario_id,
        scenario_version=record.scenario_version,
        name=scenario.name,
        formula_version=record.formula_version,
        canonicalization_version=record.canonicalization_version,
        input_hash=record.input_hash,
        geography_id=record.geography_id,
        project_id=record.project_id,
        is_synthetic=record.is_synthetic,
        reporting_currency=record.reporting_currency,
        price_year=record.price_year,
        monetary_basis=record.monetary_basis,
        validation_status=record.validation_status,
        recorded_at=record.recorded_at,
    )


def _scenario_detail(record: FinanceScenarioRecord) -> FinanceScenarioDetail:
    summary = _scenario_summary(record)
    return FinanceScenarioDetail(
        **summary.model_dump(),
        scenario=scenario_from_record(record),
    )


def _execution_or_404(
    db: Session,
    execution_id: str,
) -> FinanceCalculationExecution:
    execution = db.get(FinanceCalculationExecution, execution_id)
    if execution is None:
        raise HTTPException(status_code=404, detail="Finance execution not found.")
    return execution


def _scenario_record_or_404(
    db: Session,
    scenario_record_id: str,
) -> FinanceScenarioRecord:
    record = db.get(FinanceScenarioRecord, scenario_record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Finance scenario not found.")
    return record


def _execution_read(
    db: Session,
    execution: FinanceCalculationExecution,
) -> FinanceExecutionRead:
    record = _scenario_record_or_404(db, execution.scenario_record_id)
    result_count = db.scalar(
        select(func.count())
        .select_from(FinanceIndicatorResultRecord)
        .where(FinanceIndicatorResultRecord.execution_id == execution.id)
    )
    return FinanceExecutionRead(
        execution_id=execution.id,
        scenario_record_id=record.id,
        scenario_id=record.scenario_id,
        scenario_version=record.scenario_version,
        is_synthetic=record.is_synthetic,
        calculation_run_id=execution.calculation_run_id,
        formula_version=execution.formula_version,
        input_hash=execution.input_hash,
        canonicalization_version=execution.canonicalization_version,
        software_version=execution.software_version,
        status=execution.status,
        error_message=execution.error_message,
        started_at=execution.started_at,
        completed_at=execution.completed_at,
        indicator_count=int(result_count or 0),
    )


def _assert_references_exist(db: Session, scenario: FinanceScenario) -> None:
    if db.get(Geography, scenario.geography_id) is None:
        raise HTTPException(
            status_code=409,
            detail="Finance scenario geography does not exist.",
        )
    if scenario.project_id and db.get(Project, scenario.project_id) is None:
        raise HTTPException(
            status_code=409,
            detail="Finance scenario project does not exist.",
        )


@router.get("/scenarios", response_model=FinanceScenarioPage)
def list_finance_scenarios(
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> FinanceScenarioPage:
    """List immutable finance scenario versions in deterministic order."""
    records = list(
        db.scalars(
            select(FinanceScenarioRecord)
            .order_by(
                FinanceScenarioRecord.recorded_at,
                FinanceScenarioRecord.id,
            )
            .offset(offset)
            .limit(limit)
        )
    )
    return FinanceScenarioPage(
        items=[_scenario_summary(record) for record in records],
        limit=limit,
        offset=offset,
    )


@router.get(
    "/scenarios/{scenario_record_id}",
    response_model=FinanceScenarioDetail,
)
def get_finance_scenario(
    scenario_record_id: str,
    db: Session = Depends(get_db),
) -> FinanceScenarioDetail:
    """Return one canonical finance scenario and its immutable identity."""
    return _scenario_detail(_scenario_record_or_404(db, scenario_record_id))


@router.post(
    "/scenarios",
    response_model=FinanceScenarioDetail,
    status_code=status.HTTP_201_CREATED,
)
def create_finance_scenario(
    payload: FinanceScenario,
    response: Response,
    db: Session = Depends(get_db),
) -> FinanceScenarioDetail:
    """Persist one validated canonical finance scenario version."""
    _assert_references_exist(db, payload)
    existing = db.scalar(
        select(FinanceScenarioRecord).where(
            FinanceScenarioRecord.scenario_id == payload.scenario_id,
            FinanceScenarioRecord.scenario_version == payload.scenario_version,
        )
    )
    try:
        record = persist_finance_scenario(db, payload)
    except FinancePersistenceConflict as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except FinancePersistenceError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    if existing is not None:
        response.status_code = status.HTTP_200_OK
    return _scenario_detail(record)


@router.post(
    "/calculations",
    response_model=FinanceExecutionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_finance_calculation(
    payload: FinanceCalculationRequest,
    db: Session = Depends(get_db),
) -> FinanceExecutionRead:
    """Create a distinct immutable execution for one deterministic run identity."""
    record = _scenario_record_or_404(db, payload.scenario_record_id)
    try:
        execution = execute_scenario_record(db, record)
    except FinanceCalculationRejected as error:
        raise HTTPException(
            status_code=422,
            detail={
                "message": str(error),
                "execution_id": error.execution_id,
            },
        ) from error
    except FinancePersistenceConflict as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except FinancePersistenceError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return _execution_read(db, execution)


@router.get(
    "/executions/{execution_id}",
    response_model=FinanceExecutionRead,
)
def get_finance_execution(
    execution_id: str,
    db: Session = Depends(get_db),
) -> FinanceExecutionRead:
    """Return one immutable finance calculation execution event."""
    return _execution_read(db, _execution_or_404(db, execution_id))


@router.get(
    "/executions/{execution_id}/cash-flow",
    response_model=FinanceCashFlowResponse,
)
def get_finance_cash_flow(
    execution_id: str,
    db: Session = Depends(get_db),
) -> FinanceCashFlowResponse:
    """Return exact annual project cash flows for the execution scenario."""
    execution = _execution_or_404(db, execution_id)
    record = _scenario_record_or_404(db, execution.scenario_record_id)
    scenario = scenario_from_record(record)
    return FinanceCashFlowResponse(
        execution_id=execution.id,
        calculation_run_id=execution.calculation_run_id,
        input_hash=execution.input_hash,
        formula_version=execution.formula_version,
        software_version=execution.software_version,
        currency=scenario.reporting_currency,
        price_year=scenario.price_year,
        monetary_basis=scenario.monetary_basis,
        is_synthetic=scenario.is_synthetic,
        rows=[FinanceCashFlowYear(**row) for row in cash_flow_rows(scenario)],
    )


@router.get(
    "/executions/{execution_id}/indicators",
    response_model=FinanceIndicatorPage,
)
def get_finance_indicators(
    execution_id: str,
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> FinanceIndicatorPage:
    """Return persisted non-affordability indicators in deterministic order."""
    _execution_or_404(db, execution_id)
    records = list(
        db.scalars(
            select(FinanceIndicatorResultRecord)
            .where(
                FinanceIndicatorResultRecord.execution_id == execution_id,
                ~FinanceIndicatorResultRecord.indicator_name.like(
                    "affordability.%"
                ),
            )
            .order_by(
                FinanceIndicatorResultRecord.indicator_name,
                FinanceIndicatorResultRecord.id,
            )
            .offset(offset)
            .limit(limit)
        )
    )
    return FinanceIndicatorPage(
        items=[
            FinanceIndicatorRead(
                result_id=record.id,
                execution_id=record.execution_id,
                indicator_name=record.indicator_name,
                status=record.status,
                result=record.result_json,
                lineage=record.lineage_json,
                created_at=record.created_at,
            )
            for record in records
        ],
        limit=limit,
        offset=offset,
    )


@router.get(
    "/executions/{execution_id}/affordability",
    response_model=FinanceAffordabilityPage,
)
def get_finance_affordability(
    execution_id: str,
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> FinanceAffordabilityPage:
    """Return persisted affordability results by declared customer class."""
    _execution_or_404(db, execution_id)
    records = list(
        db.scalars(
            select(FinanceIndicatorResultRecord)
            .where(
                FinanceIndicatorResultRecord.execution_id == execution_id,
                FinanceIndicatorResultRecord.indicator_name.like(
                    "affordability.%"
                ),
            )
            .order_by(
                FinanceIndicatorResultRecord.indicator_name,
                FinanceIndicatorResultRecord.id,
            )
            .offset(offset)
            .limit(limit)
        )
    )
    return FinanceAffordabilityPage(
        items=[
            FinanceAffordabilityRead(
                result_id=record.id,
                execution_id=record.execution_id,
                indicator_name=record.indicator_name,
                customer_class_id=record.indicator_name.removeprefix(
                    "affordability."
                ),
                status=record.status,
                result=record.result_json,
                lineage=record.lineage_json,
                created_at=record.created_at,
            )
            for record in records
        ],
        limit=limit,
        offset=offset,
    )


@router.get(
    "/scenarios/{scenario_record_id}/validations",
    response_model=FinanceValidationPage,
)
def get_finance_validations(
    scenario_record_id: str,
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> FinanceValidationPage:
    """Return immutable finance validation evidence in deterministic order."""
    _scenario_record_or_404(db, scenario_record_id)
    records = list(
        db.scalars(
            select(FinanceValidationEventRecord)
            .where(
                FinanceValidationEventRecord.scenario_record_id
                == scenario_record_id
            )
            .order_by(
                FinanceValidationEventRecord.created_at,
                FinanceValidationEventRecord.id,
            )
            .offset(offset)
            .limit(limit)
        )
    )
    return FinanceValidationPage(
        items=[
            FinanceValidationRead(
                validation_event_id=record.id,
                scenario_record_id=record.scenario_record_id,
                execution_id=record.execution_id,
                status=record.status,
                message=record.message,
                checks=record.checks_json,
                created_at=record.created_at,
            )
            for record in records
        ],
        limit=limit,
        offset=offset,
    )
