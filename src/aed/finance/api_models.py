"""Typed public API contracts for transparent FIN-001 finance records."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from aed.finance.models import FinanceScenario


class FinanceAPIModel(BaseModel):
    """Strict base model for public FIN-001 API payloads."""

    model_config = ConfigDict(extra="forbid")


class FinanceScenarioSummary(FinanceAPIModel):
    scenario_record_id: str
    scenario_id: str
    scenario_version: str
    name: str
    formula_version: str
    canonicalization_version: str
    input_hash: str
    geography_id: str
    project_id: str | None
    is_synthetic: bool
    reporting_currency: str
    price_year: int
    monetary_basis: str
    validation_status: str
    recorded_at: datetime


class FinanceScenarioDetail(FinanceScenarioSummary):
    scenario: FinanceScenario


class FinanceScenarioPage(FinanceAPIModel):
    items: list[FinanceScenarioSummary]
    limit: int
    offset: int


class FinanceCalculationRequest(FinanceAPIModel):
    scenario_record_id: str = Field(min_length=1, max_length=128)


class FinanceExecutionRead(FinanceAPIModel):
    execution_id: str
    scenario_record_id: str
    scenario_id: str
    scenario_version: str
    is_synthetic: bool
    calculation_run_id: str
    formula_version: str
    input_hash: str
    canonicalization_version: str
    software_version: str
    status: str
    error_message: str | None
    started_at: datetime
    completed_at: datetime
    indicator_count: int


class FinanceCashFlowYear(FinanceAPIModel):
    year: int
    lifecycle_cost: Decimal
    project_revenue: Decimal
    net_cash_flow: Decimal
    discount_factor: Decimal
    discounted_cash_flow: Decimal


class FinanceCashFlowResponse(FinanceAPIModel):
    execution_id: str
    calculation_run_id: str
    input_hash: str
    formula_version: str
    software_version: str
    currency: str
    price_year: int
    monetary_basis: str
    is_synthetic: bool
    rows: list[FinanceCashFlowYear]


class FinanceIndicatorRead(FinanceAPIModel):
    result_id: str
    execution_id: str
    indicator_name: str
    status: str
    result: dict[str, Any]
    lineage: dict[str, Any]
    created_at: datetime


class FinanceIndicatorPage(FinanceAPIModel):
    items: list[FinanceIndicatorRead]
    limit: int
    offset: int


class FinanceAffordabilityRead(FinanceAPIModel):
    result_id: str
    execution_id: str
    indicator_name: str
    customer_class_id: str
    status: str
    result: dict[str, Any]
    lineage: dict[str, Any]
    created_at: datetime


class FinanceAffordabilityPage(FinanceAPIModel):
    items: list[FinanceAffordabilityRead]
    limit: int
    offset: int


class FinanceValidationRead(FinanceAPIModel):
    validation_event_id: str
    scenario_record_id: str
    execution_id: str | None
    status: str
    message: str
    checks: dict[str, Any]
    created_at: datetime


class FinanceValidationPage(FinanceAPIModel):
    items: list[FinanceValidationRead]
    limit: int
    offset: int
