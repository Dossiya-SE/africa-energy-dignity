"""Deterministic financial engineering for Africa Energy Dignity."""

from aed.finance.calculations import (
    CalculationError,
    DebtScheduleYear,
    affordability_metrics,
    debt_schedule,
    discounted_energy,
    discounted_payback,
    dscr,
    internal_rate_of_return,
    lifecycle_cash_flows,
    lcoe,
    loan_life_coverage_ratio,
    net_present_cost,
    npv,
    simple_payback,
)
from aed.finance.lineage import (
    attach_indicator_lineage,
    build_calculation_run_identity,
    build_indicator_lineage,
    canonical_scenario_bytes,
    scenario_input_hash,
)
from aed.finance.models import (
    CalculationRunIdentity,
    FinanceScenario,
    IndicatorLineage,
)
from aed.finance.persistence import (
    FinancePersistenceConflict,
    FinancePersistenceError,
    FinanceValidationInput,
    persist_finance_scenario,
    record_calculation_execution,
    record_finance_validation_event,
)

__all__ = [
    "CalculationError",
    "CalculationRunIdentity",
    "DebtScheduleYear",
    "FinancePersistenceConflict",
    "FinancePersistenceError",
    "FinanceScenario",
    "FinanceValidationInput",
    "IndicatorLineage",
    "affordability_metrics",
    "attach_indicator_lineage",
    "build_calculation_run_identity",
    "build_indicator_lineage",
    "canonical_scenario_bytes",
    "debt_schedule",
    "discounted_energy",
    "discounted_payback",
    "dscr",
    "internal_rate_of_return",
    "lifecycle_cash_flows",
    "lcoe",
    "loan_life_coverage_ratio",
    "net_present_cost",
    "npv",
    "persist_finance_scenario",
    "record_calculation_execution",
    "record_finance_validation_event",
    "scenario_input_hash",
    "simple_payback",
]
