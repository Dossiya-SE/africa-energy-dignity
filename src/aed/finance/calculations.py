"""Deterministic FIN-001.1 project-finance calculations."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
import math
from typing import Mapping, Sequence

from aed.finance.models import (
    FORMULA_VERSION,
    CustomerClass,
    FinanceScenario,
    FinancingComponent,
    IRRResult,
    LLCRPeriodValue,
    LLCRResult,
    MoneyBasis,
    PaybackResult,
)

ZERO = Decimal("0")
ONE = Decimal("1")
IRR_MIN_RATE = Decimal("-0.999999")
IRR_MAX_RATE = Decimal("10")
IRR_TOLERANCE = Decimal("1e-10")
IRR_MAX_ITERATIONS = 256
IRR_SCAN_POINTS = 8192
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


def _finite_decimal_values(values: Sequence[Decimal]) -> bool:
    return bool(values) and all(value.is_finite() for value in values)


def discount_factor(rate: Decimal, year: int) -> Decimal:
    """Return the end-of-period annual discount factor."""
    if not rate.is_finite() or rate <= -ONE:
        raise CalculationError("Discount rate must be finite and greater than -1.")
    if year < 0:
        raise CalculationError("Discount year cannot be negative.")
    return ONE / ((ONE + rate) ** year)


def present_value(values: Mapping[int, Decimal], rate: Decimal) -> Decimal:
    """Discount an explicitly timed value series to year zero."""
    return sum(
        (value * discount_factor(rate, year) for year, value in values.items()),
        ZERO,
    )


def periodic_npv(cash_flows: Sequence[Decimal], rate: Decimal) -> Decimal:
    """Return NPV for an ordered annual cash-flow sequence."""
    if not _finite_decimal_values(cash_flows):
        raise CalculationError("Cash flows must be a non-empty finite sequence.")
    return sum(
        (
            cash_flow * discount_factor(rate, period)
            for period, cash_flow in enumerate(cash_flows)
        ),
        ZERO,
    )


def _irr_scan_grid(lower: Decimal, upper: Decimal, points: int) -> list[Decimal]:
    """Generate a deterministic grid uniform in log(1+r), including zero."""
    lower_log = math.log1p(float(lower))
    upper_log = math.log1p(float(upper))
    rates = {
        Decimal(str(math.expm1(lower_log + (upper_log - lower_log) * i / points)))
        for i in range(points + 1)
    }
    rates.update({lower, ZERO, upper})
    return sorted(rates)


def _bisect_irr_root(
    cash_flows: Sequence[Decimal],
    lower: Decimal,
    upper: Decimal,
    tolerance: Decimal,
    residual_tolerance: Decimal,
    max_iterations: int,
) -> tuple[Decimal | None, int, Decimal | None]:
    """Solve one sign-changing IRR bracket using deterministic bisection."""
    lower_value = periodic_npv(cash_flows, lower)
    upper_value = periodic_npv(cash_flows, upper)
    if abs(lower_value) <= residual_tolerance:
        return lower, 0, lower_value
    if abs(upper_value) <= residual_tolerance:
        return upper, 0, upper_value
    if lower_value * upper_value > ZERO:
        return None, 0, None

    midpoint = lower
    midpoint_value = lower_value
    for iteration in range(1, max_iterations + 1):
        midpoint = (lower + upper) / Decimal("2")
        midpoint_value = periodic_npv(cash_flows, midpoint)
        if abs(midpoint_value) <= residual_tolerance:
            return midpoint, iteration, midpoint_value
        if lower_value * midpoint_value <= ZERO:
            upper = midpoint
            upper_value = midpoint_value
        else:
            lower = midpoint
            lower_value = midpoint_value
    return None, max_iterations, midpoint_value


def internal_rate_of_return(
    cash_flows: Sequence[Decimal],
    *,
    lower_bound: Decimal = IRR_MIN_RATE,
    upper_bound: Decimal = IRR_MAX_RATE,
    tolerance: Decimal = IRR_TOLERANCE,
    scan_points: int = IRR_SCAN_POINTS,
    max_iterations: int = IRR_MAX_ITERATIONS,
) -> IRRResult:
    """Find every admissible IRR in a bounded domain and return one only if unique."""
    method = "deterministic_bracketed_solver"
    values = tuple(cash_flows)
    base_diagnostics = {
        "domain": [lower_bound, upper_bound],
        "scan_points": scan_points,
        "max_iterations_per_bracket": max_iterations,
    }
    if (
        not _finite_decimal_values(values)
        or len(values) < 2
        or lower_bound <= -ONE
        or upper_bound <= lower_bound
        or tolerance <= ZERO
        or scan_points < 2
        or max_iterations < 1
    ):
        return IRRResult(
            value=None,
            status="invalid_cashflows",
            method=method,
            tolerance=tolerance if tolerance > ZERO else IRR_TOLERANCE,
            iterations=0,
            warnings=[
                "IRR requires finite periodic cash flows and a valid solver domain."
            ],
            diagnostics=base_diagnostics,
        )
    if not any(value < ZERO for value in values) or not any(
        value > ZERO for value in values
    ):
        return IRRResult(
            value=None,
            status="invalid_cashflows",
            method=method,
            tolerance=tolerance,
            iterations=0,
            warnings=["IRR requires at least one negative and one positive cash flow."],
            diagnostics=base_diagnostics,
        )

    scale = max(abs(value) for value in values)
    residual_tolerance = max(Decimal("1e-18"), scale * Decimal("1e-12"))
    grid = _irr_scan_grid(lower_bound, upper_bound, scan_points)
    evaluations: list[tuple[Decimal, Decimal]] = []
    for rate in grid:
        try:
            evaluations.append((rate, periodic_npv(values, rate)))
        except (CalculationError, ArithmeticError, OverflowError):
            continue

    brackets: list[tuple[Decimal, Decimal]] = []
    sampled_roots: list[Decimal] = []
    for index, (rate, value) in enumerate(evaluations):
        if abs(value) <= residual_tolerance:
            sampled_roots.append(rate)
        if index == 0:
            continue
        previous_rate, previous_value = evaluations[index - 1]
        if previous_value * value < ZERO:
            brackets.append((previous_rate, rate))

    root_records: list[tuple[Decimal, Decimal, int]] = []
    for sampled in sampled_roots:
        root_records.append((sampled, periodic_npv(values, sampled), 0))
    failed_brackets = 0
    for lower, upper in brackets:
        root, iterations, residual = _bisect_irr_root(
            values,
            lower,
            upper,
            tolerance,
            residual_tolerance,
            max_iterations,
        )
        if root is None or residual is None:
            failed_brackets += 1
            continue
        root_records.append((root, residual, iterations))

    root_records.sort(key=lambda record: record[0])
    deduplicated: list[tuple[Decimal, Decimal, int]] = []
    dedup_tolerance = tolerance * Decimal("100")
    for record in root_records:
        if not deduplicated or abs(record[0] - deduplicated[-1][0]) > dedup_tolerance:
            deduplicated.append(record)
        elif abs(record[1]) < abs(deduplicated[-1][1]):
            deduplicated[-1] = record

    diagnostics = {
        **base_diagnostics,
        "bracket_count": len(brackets),
        "failed_brackets": failed_brackets,
        "residual_tolerance": residual_tolerance,
        "roots": [record[0] for record in deduplicated],
        "residuals": [record[1] for record in deduplicated],
    }
    iterations = sum(record[2] for record in deduplicated)
    if len(deduplicated) == 1:
        return IRRResult(
            value=deduplicated[0][0],
            status="unique_root",
            method=method,
            tolerance=tolerance,
            iterations=iterations,
            diagnostics=diagnostics,
        )
    if len(deduplicated) > 1:
        return IRRResult(
            value=None,
            status="multiple_roots",
            method=method,
            tolerance=tolerance,
            iterations=iterations,
            warnings=["More than one economically admissible IRR exists."],
            diagnostics=diagnostics,
        )
    if failed_brackets:
        return IRRResult(
            value=None,
            status="non_convergent",
            method=method,
            tolerance=tolerance,
            iterations=max_iterations * failed_brackets,
            warnings=["One or more IRR brackets did not converge."],
            diagnostics=diagnostics,
        )
    return IRRResult(
        value=None,
        status="no_root",
        method=method,
        tolerance=tolerance,
        iterations=0,
        warnings=["No IRR was found inside the documented solver domain."],
        diagnostics=diagnostics,
    )


def _payback_from_series(
    cash_flows: Sequence[Decimal],
    *,
    method: str,
    no_payback_status: str,
    discount_rate: Decimal | None = None,
    diagnostics: dict[str, object] | None = None,
) -> PaybackResult:
    values = tuple(cash_flows)
    if not _finite_decimal_values(values):
        return PaybackResult(
            value=None,
            status="invalid_cashflows",
            method=method,
            discount_rate=discount_rate,
            warnings=["Payback requires a non-empty finite cash-flow sequence."],
            diagnostics=diagnostics or {},
        )

    cumulative = values[0]
    cumulative_path = [cumulative]
    if cumulative >= ZERO:
        return PaybackResult(
            value=ZERO,
            status="exact",
            method=method,
            discount_rate=discount_rate,
            diagnostics={
                **(diagnostics or {}),
                "cumulative_cash_flows": cumulative_path,
            },
        )

    for period in range(1, len(values)):
        previous = cumulative
        current_flow = values[period]
        cumulative += current_flow
        cumulative_path.append(cumulative)
        if cumulative < ZERO:
            continue
        if cumulative == ZERO:
            return PaybackResult(
                value=Decimal(period),
                status="exact",
                method=method,
                discount_rate=discount_rate,
                diagnostics={
                    **(diagnostics or {}),
                    "crossing_period": period,
                    "cumulative_cash_flows": cumulative_path,
                },
            )
        if previous < ZERO and current_flow > ZERO:
            value = Decimal(period - 1) + (-previous / current_flow)
            return PaybackResult(
                value=value,
                status="interpolated",
                method=method,
                discount_rate=discount_rate,
                diagnostics={
                    **(diagnostics or {}),
                    "crossing_period": period,
                    "previous_cumulative": previous,
                    "crossing_cash_flow": current_flow,
                    "cumulative_cash_flows": cumulative_path,
                },
            )
        return PaybackResult(
            value=None,
            status="invalid_cashflows",
            method=method,
            discount_rate=discount_rate,
            warnings=[
                "Cumulative recovery occurred without a positive crossing cash flow."
            ],
            diagnostics={
                **(diagnostics or {}),
                "crossing_period": period,
                "cumulative_cash_flows": cumulative_path,
            },
        )

    return PaybackResult(
        value=None,
        status=no_payback_status,
        method=method,
        discount_rate=discount_rate,
        warnings=["Investment is not recovered inside the analysis horizon."],
        diagnostics={**(diagnostics or {}), "cumulative_cash_flows": cumulative_path},
    )


def simple_payback(cash_flows: Sequence[Decimal]) -> PaybackResult:
    """Return first undiscounted cumulative recovery with interpolation."""
    return _payback_from_series(
        cash_flows,
        method="undiscounted_cumulative_first_crossing",
        no_payback_status="no_payback",
    )


def discounted_payback(
    cash_flows: Sequence[Decimal],
    discount_rate: Decimal,
    *,
    cash_flow_basis: MoneyBasis,
    discount_rate_basis: MoneyBasis,
) -> PaybackResult:
    """Return first discounted cumulative recovery after basis validation."""
    method = "discounted_cumulative_first_crossing"
    values = tuple(cash_flows)
    if (
        not _finite_decimal_values(values)
        or not discount_rate.is_finite()
        or discount_rate <= -ONE
        or cash_flow_basis != discount_rate_basis
    ):
        warnings = []
        if cash_flow_basis != discount_rate_basis:
            warnings.append("Cash-flow and discount-rate monetary bases must match.")
        if not discount_rate.is_finite() or discount_rate <= -ONE:
            warnings.append("Discount rate must be finite and greater than -1.")
        if not _finite_decimal_values(values):
            warnings.append("Discounted payback requires finite cash flows.")
        return PaybackResult(
            value=None,
            status="invalid_cashflows",
            method=method,
            discount_rate=discount_rate,
            warnings=warnings,
            diagnostics={
                "cash_flow_basis": cash_flow_basis,
                "discount_rate_basis": discount_rate_basis,
            },
        )

    discounted = [
        cash_flow * discount_factor(discount_rate, period)
        for period, cash_flow in enumerate(values)
    ]
    return _payback_from_series(
        discounted,
        method=method,
        no_payback_status="no_discounted_payback",
        discount_rate=discount_rate,
        diagnostics={
            "cash_flow_basis": cash_flow_basis,
            "discount_rate_basis": discount_rate_basis,
            "discounted_cash_flows": discounted,
        },
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
    fixed = (
        customer.monthly_fixed_charge.amount
        if customer.monthly_fixed_charge
        else ZERO
    )
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
        raise CalculationError(
            "Custom debt schedules require explicit payment records."
        )

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


def loan_life_coverage_ratio(
    cads_by_year: Mapping[int, Decimal],
    schedule: Sequence[DebtScheduleYear],
    debt_discount_rate: Decimal,
    *,
    cads_basis: MoneyBasis,
    debt_discount_rate_basis: MoneyBasis,
) -> LLCRResult:
    """Calculate LLCR from opening debt and CFADS inside the remaining loan life."""
    method = "opening_balance_loan_life_present_value"
    if not schedule or all(row.opening_balance == ZERO for row in schedule):
        return LLCRResult(
            status="not_applicable",
            method=method,
            discount_rate=debt_discount_rate,
            warnings=["LLCR is not applicable when no debt is outstanding."],
        )
    if (
        not debt_discount_rate.is_finite()
        or debt_discount_rate <= -ONE
        or cads_basis != debt_discount_rate_basis
    ):
        return LLCRResult(
            status="invalid_inputs",
            method=method,
            discount_rate=debt_discount_rate,
            warnings=["LLCR requires a valid debt rate and matching monetary bases."],
            diagnostics={
                "cads_basis": cads_basis,
                "debt_discount_rate_basis": debt_discount_rate_basis,
            },
        )

    ordered = sorted(schedule, key=lambda row: row.year)
    schedule_years = [row.year for row in ordered]
    if len(set(schedule_years)) != len(ordered):
        return LLCRResult(
            status="invalid_inputs",
            method=method,
            discount_rate=debt_discount_rate,
            warnings=["Debt schedule periods must be unique."],
        )
    expected_years = list(range(schedule_years[0], schedule_years[-1] + 1))
    if schedule_years != expected_years:
        return LLCRResult(
            status="invalid_inputs",
            method=method,
            discount_rate=debt_discount_rate,
            warnings=["Debt schedule periods must be consecutive annual periods."],
        )
    for index, row in enumerate(ordered):
        values = (
            row.opening_balance,
            row.interest,
            row.principal,
            row.debt_service,
            row.closing_balance,
        )
        if row.year < 1 or not all(
            value.is_finite() and value >= ZERO for value in values
        ):
            return LLCRResult(
                status="invalid_inputs",
                method=method,
                discount_rate=debt_discount_rate,
                warnings=["Debt schedule values must be finite and non-negative."],
            )
        if row.opening_balance - row.principal != row.closing_balance:
            return LLCRResult(
                status="invalid_inputs",
                method=method,
                discount_rate=debt_discount_rate,
                warnings=["Debt balance identity is inconsistent."],
            )
        if row.interest + row.principal != row.debt_service:
            return LLCRResult(
                status="invalid_inputs",
                method=method,
                discount_rate=debt_discount_rate,
                warnings=["Debt-service identity is inconsistent."],
            )
        if index and row.opening_balance != ordered[index - 1].closing_balance:
            return LLCRResult(
                status="invalid_inputs",
                method=method,
                discount_rate=debt_discount_rate,
                warnings=[
                    "Debt opening balances must reconcile to prior closing balances."
                ],
            )

    debt_rows = [row for row in ordered if row.opening_balance > ZERO]
    if not debt_rows:
        return LLCRResult(
            status="not_applicable",
            method=method,
            discount_rate=debt_discount_rate,
            warnings=["LLCR is not applicable after debt is fully repaid."],
        )
    final_debt_period = max(row.year for row in debt_rows)
    required_periods = set(range(debt_rows[0].year, final_debt_period + 1))
    if not required_periods.issubset(cads_by_year):
        missing = sorted(required_periods.difference(cads_by_year))
        return LLCRResult(
            status="invalid_inputs",
            method=method,
            discount_rate=debt_discount_rate,
            warnings=["CFADS is missing inside the remaining loan life."],
            diagnostics={"missing_periods": missing},
        )
    if any(not value.is_finite() for value in cads_by_year.values()):
        return LLCRResult(
            status="invalid_inputs",
            method=method,
            discount_rate=debt_discount_rate,
            warnings=["CFADS values must be finite."],
        )

    period_values: list[LLCRPeriodValue] = []
    numerators: dict[int, Decimal] = {}
    for row in debt_rows:
        numerator = sum(
            (
                cads_by_year[period]
                * discount_factor(debt_discount_rate, period - row.year)
                for period in range(row.year, final_debt_period + 1)
            ),
            ZERO,
        )
        numerators[row.year] = numerator
        period_values.append(
            LLCRPeriodValue(
                period=row.year,
                value=numerator / row.opening_balance,
            )
        )

    values = [item.value for item in period_values]
    ignored_periods = sorted(
        period for period in cads_by_year if period > final_debt_period
    )
    return LLCRResult(
        initial_llcr=period_values[0].value,
        minimum_llcr=min(values),
        period_values=period_values,
        status="calculated",
        method=method,
        discount_rate=debt_discount_rate,
        diagnostics={
            "final_debt_period": final_debt_period,
            "numerators": numerators,
            "ignored_post_maturity_cfads_periods": ignored_periods,
            "cads_basis": cads_basis,
            "debt_discount_rate_basis": debt_discount_rate_basis,
            "denominator": "opening_debt_balance",
        },
    )


def affordability_metrics(customer: CustomerClass) -> AffordabilityResult:
    """Calculate recurring bill burden and connection-cost burden by class."""
    income = customer.monthly_disposable_income.amount
    if income <= ZERO:
        raise CalculationError("Affordability requires positive monthly income.")
    fixed = (
        customer.monthly_fixed_charge.amount
        if customer.monthly_fixed_charge
        else ZERO
    )
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
