"""Deterministic FIN-001.1 project-finance calculations."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Mapping

from aed.finance.models import CustomerClass, FinanceScenario, FinancingComponent

ZERO = Decimal("0")
ONE = Decimal("1")
ENERGY_TO_MWH = {
    "kWh": Decimal("0.001"),
    "MWh": ONE,
    "GWh": Decimal("1000"),
}


class CalculationError(ValueError):
    """Raised when a deterministic formula precondition is not satisfied."""


@dataclass(frozen=True)
class DebtScheduleYear:
    year: int
    opening_balance: Decimal
    interest: Decimal
    principal: Decimal
    debt_service: Decimal
    closing_balance: Decimal


@dataclass(frozen=True)
class AffordabilityResult:
    customer_class_id: str
    monthly_bill: Decimal
    monthly_energy_burden: Decimal
    connection_cost_burden_months: Decimal
    currency: str
    price_year: int
    basis: str


def discount_factor(rate: Decimal, year: int) -> Decimal:
    """Return the end-of-period annual discount factor."""
    if rate < ZERO:
        raise CalculationError("Discount rate cannot be negative.")
    if year < 0:
        raise CalculationError("Discount year cannot be negative.")
    return ONE / ((ONE + rate) ** year)


def present_value(values: Mapping[int, Decimal], rate: Decimal) -> Decimal:
    """Discount an explicitly timed value series to year zero."""
    return sum(
        (value * discount_factor(rate, year) for year, value in values.items()),
        ZERO,
    )


def lifecycle_costs(scenario: FinanceScenario) -> dict[int, Decimal]:
    """Build annual economic lifecycle costs, net of positive salvage value."""
    costs = {year: ZERO for year in range(scenario.project_lifetime_years + 1)}
    for item in scenario.cost_items:
        if item.timing_year > scenario.project_lifetime_years:
            continue
        sign = Decimal("-1") if item.category == "salvage_value" else ONE
        costs[item.timing_year] += sign * item.value.amount
    return costs


def net_present_cost(scenario: FinanceScenario) -> Decimal:
    """Calculate economic lifecycle net present cost before financing transfers."""
    return present_value(lifecycle_costs(scenario), scenario.discount_rate)


def discounted_energy(scenario: FinanceScenario, unit: str = "MWh") -> Decimal:
    """Calculate discounted lifecycle energy in a controlled target unit."""
    if unit not in ENERGY_TO_MWH:
        raise CalculationError(f"Unsupported energy unit: {unit}.")
    target_to_mwh = ENERGY_TO_MWH[unit]
    total = ZERO
    for item in scenario.annual_energy:
        energy_mwh = item.energy * ENERGY_TO_MWH[item.unit]
        target_energy = energy_mwh / target_to_mwh
        total += target_energy * discount_factor(scenario.discount_rate, item.year)
    return total


def lcoe(scenario: FinanceScenario, unit: str = "MWh") -> Decimal:
    """Calculate levelized cost per discounted energy unit."""
    energy = discounted_energy(scenario, unit)
    if energy <= ZERO:
        raise CalculationError("LCOE is undefined when discounted energy is zero.")
    return net_present_cost(scenario) / energy


def _annual_customer_revenue(customer: CustomerClass) -> Decimal:
    fixed = customer.monthly_fixed_charge.amount if customer.monthly_fixed_charge else ZERO
    energy_revenue = (
        customer.annual_consumption_per_customer
        * customer.tariff_per_energy.amount
    )
    return Decimal(customer.customer_count) * (energy_revenue + Decimal("12") * fixed)


def lifecycle_cash_flows(scenario: FinanceScenario) -> dict[int, Decimal]:
    """Build project cash flows before financing from costs and customer revenue."""
    costs = lifecycle_costs(scenario)
    annual_revenue = sum(
        (_annual_customer_revenue(customer) for customer in scenario.customer_classes),
        ZERO,
    )
    cash_flows: dict[int, Decimal] = {}
    for year in range(scenario.project_lifetime_years + 1):
        revenue = annual_revenue if year > 0 else ZERO
        cash_flows[year] = revenue - costs[year]
    return cash_flows


def npv(scenario: FinanceScenario) -> Decimal:
    """Calculate project NPV before financing."""
    return present_value(lifecycle_cash_flows(scenario), scenario.discount_rate)


def break_even_tariff(
    scenario: FinanceScenario,
    billable_energy_unit: str = "MWh",
) -> Decimal:
    """Return the constant energy tariff that gives project NPV equal to zero."""
    energy = discounted_energy(scenario, billable_energy_unit)
    if energy <= ZERO:
        raise CalculationError("Break-even tariff requires positive discounted energy.")
    return net_present_cost(scenario) / energy


def required_subsidy(
    npv_without_subsidy: Decimal,
    discount_rate: Decimal,
    payment_year: int = 0,
) -> Decimal:
    """Return a non-negative subsidy at the declared payment year for zero NPV."""
    subsidy = -npv_without_subsidy / discount_factor(discount_rate, payment_year)
    return max(ZERO, subsidy)


def debt_schedule(component: FinancingComponent) -> list[DebtScheduleYear]:
    """Generate a deterministic annual schedule for one debt component."""
    if component.type != "debt":
        raise CalculationError("Debt schedule requires a debt financing component.")
    if component.repayment_profile == "custom":
        raise CalculationError("Custom debt schedules require explicit payment records.")

    principal = component.amount.amount
    rate = component.interest_rate
    tenor = component.tenor_years
    grace = component.grace_period_years
    if rate is None or tenor is None or grace is None:
        raise CalculationError("Debt component is missing required terms.")

    amortizing_periods = tenor - grace
    level_principal = principal / Decimal(amortizing_periods)
    if rate == ZERO:
        annuity_payment = level_principal
    else:
        growth = (ONE + rate) ** amortizing_periods
        annuity_payment = principal * rate * growth / (growth - ONE)

    balance = principal
    rows: list[DebtScheduleYear] = []
    for year in range(1, tenor + 1):
        opening = balance
        interest = opening * rate
        planned_principal = ZERO
        if year > grace:
            if component.repayment_profile == "level_principal":
                planned_principal = level_principal
            elif component.repayment_profile == "annuity":
                planned_principal = annuity_payment - interest
            elif component.repayment_profile == "bullet" and year == tenor:
                planned_principal = opening
        principal_paid = min(opening, max(ZERO, planned_principal))
        if year == tenor:
            principal_paid = opening
        closing = opening - principal_paid
        if closing < ZERO:
            raise CalculationError("Debt principal became negative.")
        rows.append(
            DebtScheduleYear(
                year=year,
                opening_balance=opening,
                interest=interest,
                principal=principal_paid,
                debt_service=interest + principal_paid,
                closing_balance=closing,
            )
        )
        balance = closing

    if balance != ZERO:
        raise CalculationError("Debt schedule does not close to zero.")
    return rows


def dscr(
    cads_by_year: Mapping[int, Decimal],
    schedule: list[DebtScheduleYear],
) -> dict[int, Decimal]:
    """Calculate DSCR only in years with positive debt service."""
    results: dict[int, Decimal] = {}
    for row in schedule:
        if row.debt_service <= ZERO:
            continue
        if row.year not in cads_by_year:
            raise CalculationError(f"CADS is missing for debt-service year {row.year}.")
        results[row.year] = cads_by_year[row.year] / row.debt_service
    return results


def affordability_metrics(customer: CustomerClass) -> AffordabilityResult:
    """Calculate recurring bill burden and connection-cost burden by class."""
    income = customer.monthly_disposable_income.amount
    if income <= ZERO:
        raise CalculationError("Affordability requires positive monthly income.")
    fixed = customer.monthly_fixed_charge.amount if customer.monthly_fixed_charge else ZERO
    monthly_energy_charge = (
        customer.annual_consumption_per_customer
        * customer.tariff_per_energy.amount
        / Decimal("12")
    )
    bill = monthly_energy_charge + fixed
    return AffordabilityResult(
        customer_class_id=customer.customer_class_id,
        monthly_bill=bill,
        monthly_energy_burden=bill / income,
        connection_cost_burden_months=customer.connection_charge.amount / income,
        currency=customer.monthly_disposable_income.currency,
        price_year=customer.monthly_disposable_income.price_year,
        basis=customer.monthly_disposable_income.basis,
    )
