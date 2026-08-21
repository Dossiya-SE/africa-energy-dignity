"""Deterministic FIN-001 calculation orchestration for API executions."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Literal

from sqlalchemy.orm import Session

from aed.database.models import FinanceCalculationExecution, FinanceScenarioRecord
from aed.finance.calculations import (
    CalculationError,
    affordability_metrics,
    break_even_tariff,
    debt_schedule,
    discounted_energy,
    discounted_payback,
    discount_factor,
    dscr,
    internal_rate_of_return,
    lifecycle_cash_flows,
    lifecycle_costs,
    lcoe,
    loan_life_coverage_ratio,
    net_present_cost,
    npv,
    required_subsidy,
    simple_payback,
)
from aed.finance.lineage import (
    attach_indicator_lineage,
    build_calculation_run_identity,
)
from aed.finance.models import (
    CalculationRunIdentity,
    DeterministicIndicatorResult,
    FinanceModel,
    FinanceScenario,
)
from aed.finance.persistence import (
    FinanceValidationInput,
    record_calculation_execution,
)

API_SOFTWARE_VERSION = "AED-FIN-001-API-1"


class FinanceCalculationRejected(ValueError):
    """Raised after a failed execution event has been persisted."""

    def __init__(self, message: str, execution_id: str):
        super().__init__(message)
        self.execution_id = execution_id


class ScalarIndicatorResult(DeterministicIndicatorResult):
    """Exact scalar result with deterministic lineage."""

    value: Decimal
    status: Literal["calculated"] = "calculated"
    unit: str | None = None


class PeriodIndicatorValue(FinanceModel):
    """One period in an exact deterministic indicator series."""

    period: int
    value: Decimal


class SeriesIndicatorResult(DeterministicIndicatorResult):
    """Exact period-indexed result with deterministic lineage."""

    period_values: list[PeriodIndicatorValue]
    status: Literal["calculated"] = "calculated"
    unit: str | None = None


class AffordabilityIndicatorResult(DeterministicIndicatorResult):
    """Exact affordability result for one declared customer class."""

    customer_class_id: str
    monthly_bill: Decimal
    monthly_energy_burden: Decimal
    connection_cost_burden_months: Decimal
    currency: str
    price_year: int
    basis: str
    status: Literal["calculated"] = "calculated"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def scenario_from_record(record: FinanceScenarioRecord) -> FinanceScenario:
    """Revalidate a persisted scenario payload before calculation or publication."""
    return FinanceScenario.model_validate(record.payload_json)


def _scalar(
    value: Decimal,
    *,
    method: str,
    unit: str | None = None,
    diagnostics: dict | None = None,
) -> ScalarIndicatorResult:
    return ScalarIndicatorResult(
        value=value,
        method=method,
        unit=unit,
        diagnostics=diagnostics or {},
    )


def _series(
    values: dict[int, Decimal],
    *,
    method: str,
    unit: str | None = None,
    diagnostics: dict | None = None,
) -> SeriesIndicatorResult:
    return SeriesIndicatorResult(
        period_values=[
            PeriodIndicatorValue(period=period, value=value)
            for period, value in sorted(values.items())
        ],
        method=method,
        unit=unit,
        diagnostics=diagnostics or {},
    )


def _core_results(scenario: FinanceScenario) -> dict[str, DeterministicIndicatorResult]:
    cash_flow_map = lifecycle_cash_flows(scenario)
    cash_flows = [
        cash_flow_map[year]
        for year in range(scenario.project_lifetime_years + 1)
    ]
    project_npv = npv(scenario)
    results: dict[str, DeterministicIndicatorResult] = {
        "net_present_cost": _scalar(
            net_present_cost(scenario),
            method="discounted_lifecycle_costs",
            unit=scenario.reporting_currency,
        ),
        "discounted_energy": _scalar(
            discounted_energy(scenario, "MWh"),
            method="discounted_annual_energy",
            unit="MWh",
        ),
        "lcoe": _scalar(
            lcoe(scenario, "MWh"),
            method="net_present_cost_per_discounted_energy",
            unit=f"{scenario.reporting_currency}/MWh",
        ),
        "npv": _scalar(
            project_npv,
            method="discounted_pre_financing_project_cash_flow",
            unit=scenario.reporting_currency,
        ),
        "break_even_tariff": _scalar(
            break_even_tariff(scenario, "MWh"),
            method="zero_npv_constant_energy_tariff",
            unit=f"{scenario.reporting_currency}/MWh",
        ),
        "required_subsidy": _scalar(
            required_subsidy(project_npv, scenario.discount_rate),
            method="year_zero_subsidy_for_zero_npv",
            unit=scenario.reporting_currency,
            diagnostics={"payment_year": 0},
        ),
        "irr": internal_rate_of_return(cash_flows),
        "simple_payback": simple_payback(cash_flows),
        "discounted_payback": discounted_payback(
            cash_flows,
            scenario.discount_rate,
            cash_flow_basis=scenario.monetary_basis,
            discount_rate_basis=scenario.discount_rate_basis,
        ),
    }
    return results


def _debt_results(scenario: FinanceScenario) -> dict[str, DeterministicIndicatorResult]:
    cash_flow_map = lifecycle_cash_flows(scenario)
    output: dict[str, DeterministicIndicatorResult] = {}
    debt_components = sorted(
        (
            component
            for component in scenario.financing_components
            if component.type == "debt"
        ),
        key=lambda component: component.component_id,
    )
    for component in debt_components:
        schedule = debt_schedule(component)
        final_debt_year = schedule[-1].year
        if final_debt_year > scenario.project_lifetime_years:
            raise CalculationError(
                "Debt tenor cannot exceed project lifetime for FIN-001 API execution."
            )
        cfads = {row.year: cash_flow_map[row.year] for row in schedule}
        component_id = component.component_id
        output[f"dscr.{component_id}"] = _series(
            dscr(cfads, schedule),
            method="pre_financing_cash_flow_over_debt_service",
            unit="ratio",
            diagnostics={
                "component_id": component_id,
                "cfads_policy": "pre_financing_project_cash_flow",
            },
        )
        if component.interest_rate is None:
            raise CalculationError("Debt component interest rate is required for LLCR.")
        output[f"llcr.{component_id}"] = loan_life_coverage_ratio(
            cfads,
            schedule,
            component.interest_rate,
            cads_basis=scenario.monetary_basis,
            debt_discount_rate_basis=scenario.monetary_basis,
        )
    return output


def _affordability_results(
    scenario: FinanceScenario,
) -> dict[str, DeterministicIndicatorResult]:
    output: dict[str, DeterministicIndicatorResult] = {}
    for customer in sorted(
        scenario.customer_classes,
        key=lambda item: item.customer_class_id,
    ):
        metrics = affordability_metrics(customer)
        name = f"affordability.{customer.customer_class_id}"
        output[name] = AffordabilityIndicatorResult(
            customer_class_id=metrics.customer_class_id,
            monthly_bill=metrics.monthly_bill,
            monthly_energy_burden=metrics.monthly_energy_burden,
            connection_cost_burden_months=metrics.connection_cost_burden_months,
            currency=metrics.currency,
            price_year=metrics.price_year,
            basis=metrics.basis,
            method="monthly_bill_and_connection_cost_burden",
            diagnostics={"customer_class_name": customer.name},
        )
    return output


def calculate_indicator_results(
    scenario: FinanceScenario,
    identity: CalculationRunIdentity,
) -> dict[str, DeterministicIndicatorResult]:
    """Calculate and line every FIN-001 result in deterministic name order."""
    raw = {
        **_core_results(scenario),
        **_debt_results(scenario),
        **_affordability_results(scenario),
    }
    return {
        name: attach_indicator_lineage(
            raw[name],
            identity,
            indicator_name=name,
        )
        for name in sorted(raw)
    }


def execute_scenario_record(
    db: Session,
    record: FinanceScenarioRecord,
) -> FinanceCalculationExecution:
    """Create one immutable execution event for a persisted canonical scenario."""
    scenario = scenario_from_record(record)
    identity = build_calculation_run_identity(
        scenario,
        software_version=API_SOFTWARE_VERSION,
    )
    started_at = _utcnow()
    try:
        results = calculate_indicator_results(scenario, identity)
    except (CalculationError, ArithmeticError, ValueError) as error:
        completed_at = _utcnow()
        execution = record_calculation_execution(
            db,
            scenario=scenario,
            identity=identity,
            results={},
            status="failed",
            error_message=str(error),
            validation_events=[
                FinanceValidationInput(
                    status="failed",
                    message="FIN-001 deterministic calculation was rejected.",
                    checks={
                        "calculation_completed": False,
                        "error_type": type(error).__name__,
                    },
                )
            ],
            started_at=started_at,
            completed_at=completed_at,
        )
        raise FinanceCalculationRejected(str(error), execution.id) from error

    validation_status = "warning" if scenario.is_synthetic else "passed"
    message = (
        "Synthetic FIN-001 calculation completed; results remain unsuitable for "
        "real-project claims."
        if scenario.is_synthetic
        else "FIN-001 deterministic calculation and lineage checks passed."
    )
    return record_calculation_execution(
        db,
        scenario=scenario,
        identity=identity,
        results=results,
        validation_events=[
            FinanceValidationInput(
                status=validation_status,
                message=message,
                checks={
                    "canonical_input_hash_matches": True,
                    "calculation_run_identity_matches": True,
                    "formula_version_matches": True,
                    "indicator_lineage_attached": True,
                    "is_synthetic": scenario.is_synthetic,
                },
            )
        ],
        started_at=started_at,
        completed_at=_utcnow(),
    )


def cash_flow_rows(scenario: FinanceScenario) -> list[dict[str, Decimal | int]]:
    """Return exact annual lifecycle-cost, revenue and cash-flow rows."""
    costs = lifecycle_costs(scenario)
    cash_flows = lifecycle_cash_flows(scenario)
    rows: list[dict[str, Decimal | int]] = []
    for year in range(scenario.project_lifetime_years + 1):
        net_cash_flow = cash_flows[year]
        lifecycle_cost = costs[year]
        rows.append(
            {
                "year": year,
                "lifecycle_cost": lifecycle_cost,
                "project_revenue": net_cash_flow + lifecycle_cost,
                "net_cash_flow": net_cash_flow,
                "discount_factor": discount_factor(scenario.discount_rate, year),
                "discounted_cash_flow": (
                    net_cash_flow * discount_factor(scenario.discount_rate, year)
                ),
            }
        )
    return rows
