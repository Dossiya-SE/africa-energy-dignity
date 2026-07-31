"""Typed FIN-001 finance inputs, outputs and integrity controls."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

FORMULA_VERSION = "FIN-001.1"
PERIOD_BASIS = "annual"

EvidenceClass = Literal[
    "observed",
    "published",
    "derived",
    "assumed",
    "scenario",
    "expert_judgment",
    "unverified",
]
ValidationStatus = Literal[
    "proposed",
    "schema_valid",
    "source_verified",
    "cross_checked",
    "model_ready",
    "validated",
    "rejected",
    "deprecated",
]
MoneyBasis = Literal["real", "nominal"]
CostCategory = Literal[
    "capex",
    "fixed_opex",
    "variable_opex",
    "fuel",
    "replacement",
    "tax",
    "duty",
    "decommissioning",
    "salvage_value",
]
FinancingType = Literal["debt", "equity", "grant", "subsidy"]
RepaymentProfile = Literal["level_principal", "annuity", "bullet", "custom"]
EnergyUnit = Literal["kWh", "MWh", "GWh"]
IRRStatus = Literal[
    "unique_root",
    "no_root",
    "multiple_roots",
    "invalid_cashflows",
    "non_convergent",
]
PaybackStatus = Literal[
    "exact",
    "interpolated",
    "no_payback",
    "no_discounted_payback",
    "invalid_cashflows",
]
LLCRStatus = Literal["calculated", "not_applicable", "invalid_inputs"]

VERIFIED_STATES = {
    "source_verified",
    "cross_checked",
    "model_ready",
    "validated",
}
ID_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]*$"


class FinanceModel(BaseModel):
    """Strict base model for deterministic finance records."""

    model_config = ConfigDict(extra="forbid")


class DeterministicIndicatorResult(FinanceModel):
    """Common auditable metadata returned by deterministic indicators."""

    method: str = Field(min_length=1)
    formula_version: Literal["FIN-001.1"] = FORMULA_VERSION
    period_basis: Literal["annual"] = PERIOD_BASIS
    warnings: list[str] = Field(default_factory=list)
    diagnostics: dict[str, Any] = Field(default_factory=dict)


class IRRResult(DeterministicIndicatorResult):
    value: Decimal | None = None
    status: IRRStatus
    tolerance: Decimal = Field(gt=0)
    iterations: int = Field(default=0, ge=0)


class PaybackResult(DeterministicIndicatorResult):
    value: Decimal | None = None
    status: PaybackStatus
    discount_rate: Decimal | None = None


class LLCRPeriodValue(FinanceModel):
    period: int = Field(ge=1)
    value: Decimal


class LLCRResult(DeterministicIndicatorResult):
    initial_llcr: Decimal | None = None
    minimum_llcr: Decimal | None = None
    period_values: list[LLCRPeriodValue] = Field(default_factory=list)
    status: LLCRStatus
    discount_rate: Decimal


class Money(FinanceModel):
    amount: Decimal = Field(ge=0)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    price_year: int = Field(ge=1900, le=2200)
    basis: MoneyBasis

    def assert_matches(
        self,
        currency: str,
        price_year: int,
        basis: MoneyBasis,
        label: str,
    ) -> None:
        """Reject implicit currency, price-year or basis transformations."""
        if self.currency != currency:
            raise ValueError(
                f"{label} currency {self.currency} does not match {currency}."
            )
        if self.price_year != price_year:
            raise ValueError(
                f"{label} price year {self.price_year} does not match {price_year}."
            )
        if self.basis != basis:
            raise ValueError(f"{label} basis {self.basis} does not match {basis}.")


class Uncertainty(FinanceModel):
    type: Literal["range", "confidence_interval", "scenario"]
    lower: Decimal
    upper: Decimal

    @model_validator(mode="after")
    def validate_interval(self):
        if self.upper < self.lower:
            raise ValueError(
                "Uncertainty upper bound must not be below its lower bound."
            )
        return self


class EvidenceReference(FinanceModel):
    source_id: str | None = Field(default=None, pattern=ID_PATTERN)
    evidence_class: EvidenceClass
    validation_status: ValidationStatus
    responsible_contributor: str = Field(min_length=1)
    limitations: list[str] = Field(min_length=1)
    uncertainty: Uncertainty | None = None

    @model_validator(mode="after")
    def enforce_evidence_contract(self):
        if self.evidence_class in {"observed", "published"} and not self.source_id:
            raise ValueError(
                "Observed or published finance evidence requires source_id."
            )
        if (
            self.evidence_class == "unverified"
            and self.validation_status in VERIFIED_STATES
        ):
            raise ValueError("Unverified finance evidence cannot be marked verified.")
        return self


class CostItem(FinanceModel):
    cost_id: str = Field(pattern=ID_PATTERN)
    category: CostCategory
    timing_year: int = Field(ge=0)
    value: Money
    quantity_driver: Decimal | None = Field(default=None, ge=0)
    quantity_unit: str | None = Field(default=None, min_length=1)
    evidence: EvidenceReference


class EnergyYear(FinanceModel):
    year: int = Field(ge=1)
    energy: Decimal = Field(ge=0)
    unit: EnergyUnit
    evidence: EvidenceReference


class FinancingComponent(FinanceModel):
    component_id: str = Field(pattern=ID_PATTERN)
    type: FinancingType
    amount: Money
    interest_rate: Decimal | None = Field(default=None, ge=0, le=1)
    tenor_years: int | None = Field(default=None, ge=1)
    grace_period_years: int | None = Field(default=None, ge=0)
    repayment_profile: RepaymentProfile | None = None
    evidence: EvidenceReference

    @model_validator(mode="after")
    def validate_debt_terms(self):
        if self.type != "debt":
            return self
        required = (
            self.interest_rate,
            self.tenor_years,
            self.grace_period_years,
            self.repayment_profile,
        )
        if any(value is None for value in required):
            raise ValueError("Debt requires rate, tenor, grace period and profile.")
        if self.grace_period_years >= self.tenor_years:
            raise ValueError("Debt grace period must be shorter than its tenor.")
        return self


class CustomerClass(FinanceModel):
    customer_class_id: str = Field(pattern=ID_PATTERN)
    name: str = Field(min_length=1)
    customer_count: int = Field(ge=0)
    annual_consumption_per_customer: Decimal = Field(ge=0)
    energy_unit: Literal["kWh", "MWh"]
    tariff_per_energy: Money
    monthly_fixed_charge: Money | None = None
    monthly_disposable_income: Money
    connection_charge: Money
    evidence: EvidenceReference


class FinanceScenario(FinanceModel):
    """Canonical deterministic finance scenario for formula version FIN-001.1."""

    scenario_id: str = Field(pattern=ID_PATTERN)
    name: str = Field(min_length=1)
    scenario_version: str = Field(min_length=1)
    formula_version: str = Field(min_length=1)
    geography_id: str = Field(pattern=ID_PATTERN)
    project_id: str | None = Field(default=None, pattern=ID_PATTERN)
    is_synthetic: bool
    reporting_currency: str = Field(pattern=r"^[A-Z]{3}$")
    price_year: int = Field(ge=1900, le=2200)
    monetary_basis: MoneyBasis
    discount_rate: Decimal = Field(ge=0, le=1)
    discount_rate_basis: MoneyBasis
    inflation_rate: Decimal | None = Field(default=None, ge=0, le=1)
    funding_requirement: Money
    project_start_year: int = Field(ge=1900, le=2200)
    project_lifetime_years: int = Field(ge=1)
    construction_years: int = Field(default=0, ge=0)
    cost_items: list[CostItem] = Field(min_length=1)
    annual_energy: list[EnergyYear] = Field(min_length=1)
    financing_components: list[FinancingComponent] = Field(min_length=1)
    customer_classes: list[CustomerClass] = Field(default_factory=list)
    validation_status: ValidationStatus
    responsible_contributor: str = Field(min_length=1)
    created_at: datetime
    updated_at: datetime

    def _assert_money(self, value: Money, label: str) -> None:
        value.assert_matches(
            self.reporting_currency,
            self.price_year,
            self.monetary_basis,
            label,
        )

    @model_validator(mode="after")
    def enforce_scenario_contract(self):
        if self.formula_version != FORMULA_VERSION:
            raise ValueError(
                "FIN-001 currently accepts formula_version FIN-001.1 only."
            )
        if self.discount_rate_basis != self.monetary_basis:
            raise ValueError("Cash-flow and discount-rate bases must match.")
        if self.monetary_basis == "nominal" and self.inflation_rate is None:
            raise ValueError("Nominal scenarios require an explicit inflation rate.")
        if not self.is_synthetic and not self.project_id:
            raise ValueError("A non-synthetic finance scenario requires project_id.")
        if self.funding_requirement.amount <= 0:
            raise ValueError("Funding requirement must be strictly positive.")

        self._assert_money(self.funding_requirement, "funding_requirement")
        for cost in self.cost_items:
            self._assert_money(cost.value, cost.cost_id)
        for component in self.financing_components:
            self._assert_money(component.amount, component.component_id)
        for customer in self.customer_classes:
            self._assert_money(
                customer.tariff_per_energy,
                f"{customer.customer_class_id}.tariff_per_energy",
            )
            self._assert_money(
                customer.monthly_disposable_income,
                f"{customer.customer_class_id}.monthly_disposable_income",
            )
            self._assert_money(
                customer.connection_charge,
                f"{customer.customer_class_id}.connection_charge",
            )
            if customer.monthly_fixed_charge is not None:
                self._assert_money(
                    customer.monthly_fixed_charge,
                    f"{customer.customer_class_id}.monthly_fixed_charge",
                )

        energy_years = [item.year for item in self.annual_energy]
        if len(energy_years) != len(set(energy_years)):
            raise ValueError("Annual energy contains duplicate years.")
        if any(year > self.project_lifetime_years for year in energy_years):
            raise ValueError("Annual energy cannot extend beyond project lifetime.")

        identifiers = [item.cost_id for item in self.cost_items]
        identifiers.extend(item.component_id for item in self.financing_components)
        identifiers.extend(item.customer_class_id for item in self.customer_classes)
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("Finance scenario stable identifiers must be unique.")

        financed = sum(
            (item.amount.amount for item in self.financing_components),
            Decimal("0"),
        )
        required = self.funding_requirement.amount
        tolerance = max(Decimal("0.01"), abs(required) * Decimal("1e-9"))
        if abs(financed - required) > tolerance:
            raise ValueError(
                "Financing components do not reconcile to funding requirement."
            )
        return self
