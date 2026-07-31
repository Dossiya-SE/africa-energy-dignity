"""Deterministic financial engineering for Africa Energy Dignity."""

from aed.finance.calculations import (
    CalculationError,
    DebtScheduleYear,
    affordability_metrics,
    debt_schedule,
    discounted_energy,
    dscr,
    lifecycle_cash_flows,
    lcoe,
    net_present_cost,
    npv,
)
from aed.finance.models import FinanceScenario

__all__ = [
    "CalculationError",
    "DebtScheduleYear",
    "FinanceScenario",
    "affordability_metrics",
    "debt_schedule",
    "discounted_energy",
    "dscr",
    "lifecycle_cash_flows",
    "lcoe",
    "net_present_cost",
    "npv",
]
