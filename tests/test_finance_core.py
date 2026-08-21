"""Hand-calculated verification tests for the FIN-001.1 deterministic core."""
from datetime import datetime, timezone
from decimal import Decimal
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from pydantic import ValidationError

from aed.finance.calculations import (
    CalculationError,
    DebtScheduleYear,
    affordability_metrics,
    debt_schedule,
    discounted_payback,
    dscr,
    internal_rate_of_return,
    lcoe,
    loan_life_coverage_ratio,
    net_present_cost,
    npv,
    periodic_npv,
    simple_payback,
)
from aed.finance.models import (
    CostItem,
    CustomerClass,
    EnergyYear,
    EvidenceReference,
    FinanceScenario,
    FinancingComponent,
    Money,
)

NOW = datetime(2026, 7, 31, tzinfo=timezone.utc)


def evidence() -> EvidenceReference:
    return EvidenceReference(
        evidence_class="scenario",
        validation_status="schema_valid",
        responsible_contributor="Synthetic AED reviewer",
        limitations=["Synthetic value used only for deterministic verification."],
    )


def money(amount: str, currency: str = "XOF", basis: str = "real") -> Money:
    return Money(
        amount=Decimal(amount),
        currency=currency,
        price_year=2026,
        basis=basis,
    )


def base_scenario(
    *,
    discount_rate: str = "0",
    costs: list[CostItem] | None = None,
    energy: list[EnergyYear] | None = None,
    customers: list[CustomerClass] | None = None,
    financing: list[FinancingComponent] | None = None,
) -> FinanceScenario:
    cost_items = costs or [
        CostItem(
            cost_id="cost.synthetic.capex",
            category="capex",
            timing_year=0,
            value=money("100"),
            evidence=evidence(),
        )
    ]
    annual_energy = energy or [
        EnergyYear(year=1, energy=Decimal("10"), unit="MWh", evidence=evidence()),
        EnergyYear(year=2, energy=Decimal("10"), unit="MWh", evidence=evidence()),
        EnergyYear(year=3, energy=Decimal("10"), unit="MWh", evidence=evidence()),
    ]
    components = financing or [
        FinancingComponent(
            component_id="finance.synthetic.equity",
            type="equity",
            amount=money("100"),
            evidence=evidence(),
        )
    ]
    return FinanceScenario(
        scenario_id="finance.scenario.synthetic.v1",
        name="Synthetic finance fixture",
        scenario_version="1.0.0",
        formula_version="FIN-001.1",
        geography_id="geo.bfa",
        is_synthetic=True,
        reporting_currency="XOF",
        price_year=2026,
        monetary_basis="real",
        discount_rate=Decimal(discount_rate),
        discount_rate_basis="real",
        funding_requirement=money("100"),
        project_start_year=2026,
        project_lifetime_years=3,
        construction_years=0,
        cost_items=cost_items,
        annual_energy=annual_energy,
        financing_components=components,
        customer_classes=customers or [],
        validation_status="schema_valid",
        responsible_contributor="Synthetic AED reviewer",
        created_at=NOW,
        updated_at=NOW,
    )


def debt_component(profile: str, amount: str = "90") -> FinancingComponent:
    return FinancingComponent(
        component_id=f"finance.synthetic.{profile}",
        type="debt",
        amount=money(amount),
        interest_rate=Decimal("0.10"),
        tenor_years=3,
        grace_period_years=0,
        repayment_profile=profile,
        evidence=evidence(),
    )


def test_finance_schema_and_embedded_example_validate():
    schema = json.loads(Path("schemas/finance.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for example in schema["examples"]:
        validator.validate(example)


def test_currency_mismatch_is_rejected():
    payload = base_scenario().model_dump()
    payload["cost_items"][0]["value"]["currency"] = "USD"
    with pytest.raises(ValidationError, match="currency USD does not match XOF"):
        FinanceScenario.model_validate(payload)


def test_nominal_real_basis_mismatch_is_rejected():
    payload = base_scenario().model_dump()
    payload["discount_rate_basis"] = "nominal"
    with pytest.raises(ValidationError, match="Cash-flow and discount-rate bases"):
        FinanceScenario.model_validate(payload)


def test_financing_must_reconcile_to_declared_requirement():
    payload = base_scenario().model_dump()
    payload["financing_components"][0]["amount"]["amount"] = Decimal("99")
    with pytest.raises(ValidationError, match="do not reconcile"):
        FinanceScenario.model_validate(payload)


def test_lifecycle_cost_excludes_events_after_horizon_and_discounts_salvage():
    costs = [
        CostItem(
            cost_id="cost.capex",
            category="capex",
            timing_year=0,
            value=money("100"),
            evidence=evidence(),
        ),
        CostItem(
            cost_id="cost.salvage",
            category="salvage_value",
            timing_year=1,
            value=money("11"),
            evidence=evidence(),
        ),
        CostItem(
            cost_id="cost.replacement.after-life",
            category="replacement",
            timing_year=4,
            value=money("50"),
            evidence=evidence(),
        ),
    ]
    scenario = base_scenario(discount_rate="0.10", costs=costs)
    assert net_present_cost(scenario) == Decimal("90")


def test_lcoe_reproduces_hand_calculation():
    scenario = base_scenario()
    assert lcoe(scenario, "MWh") == Decimal("100") / Decimal("30")


def test_zero_discounted_energy_blocks_lcoe():
    energy = [
        EnergyYear(year=1, energy=Decimal("0"), unit="MWh", evidence=evidence())
    ]
    with pytest.raises(CalculationError, match="discounted energy is zero"):
        lcoe(base_scenario(energy=energy))


def test_npv_reproduces_hand_calculated_customer_revenue():
    customer = CustomerClass(
        customer_class_id="customer.synthetic.household",
        name="Synthetic household",
        customer_count=1,
        annual_consumption_per_customer=Decimal("1"),
        energy_unit="MWh",
        tariff_per_energy=money("50"),
        monthly_fixed_charge=None,
        monthly_disposable_income=money("100"),
        connection_charge=money("200"),
        evidence=evidence(),
    )
    scenario = base_scenario(customers=[customer])
    assert npv(scenario) == Decimal("50")


def test_level_principal_debt_schedule_and_dscr_reconcile():
    rows = debt_schedule(debt_component("level_principal"))
    assert [row.opening_balance for row in rows] == [
        Decimal("90"),
        Decimal("60"),
        Decimal("30"),
    ]
    assert [row.interest for row in rows] == [
        Decimal("9.00"),
        Decimal("6.00"),
        Decimal("3.00"),
    ]
    assert [row.principal for row in rows] == [
        Decimal("30"),
        Decimal("30"),
        Decimal("30"),
    ]
    assert rows[-1].closing_balance == Decimal("0")

    results = dscr(
        {1: Decimal("50"), 2: Decimal("50"), 3: Decimal("50")},
        rows,
    )
    assert results[1] == Decimal("50") / Decimal("39.00")
    assert results[2] == Decimal("50") / Decimal("36.00")
    assert results[3] == Decimal("50") / Decimal("33.00")


def test_affordability_preserves_customer_class_and_units():
    customer = CustomerClass(
        customer_class_id="customer.synthetic.household",
        name="Synthetic household",
        customer_count=1,
        annual_consumption_per_customer=Decimal("120"),
        energy_unit="kWh",
        tariff_per_energy=money("2"),
        monthly_fixed_charge=money("10"),
        monthly_disposable_income=money("100"),
        connection_charge=money("300"),
        evidence=evidence(),
    )
    result = affordability_metrics(customer)
    assert result.customer_class_id == customer.customer_class_id
    assert result.monthly_bill == Decimal("30")
    assert result.monthly_energy_burden == Decimal("0.3")
    assert result.connection_cost_burden_months == Decimal("3")
    assert result.currency == "XOF"


# IRR policy


def test_irr_conventional_cash_flow_has_known_unique_root():
    result = internal_rate_of_return(
        [Decimal("-100"), Decimal("0"), Decimal("121")]
    )
    assert result.status == "unique_root"
    assert result.value == pytest.approx(Decimal("0.10"), abs=Decimal("1e-9"))
    assert result.method == "deterministic_bracketed_solver"
    assert result.formula_version == "FIN-001.1"


def test_irr_requires_positive_and_negative_cash_flows():
    assert internal_rate_of_return([Decimal("-100"), Decimal("-1")]).status == (
        "invalid_cashflows"
    )
    assert internal_rate_of_return([Decimal("0"), Decimal("100")]).status == (
        "invalid_cashflows"
    )


def test_irr_detects_multiple_admissible_roots_without_selecting_one():
    result = internal_rate_of_return(
        [Decimal("-100"), Decimal("230"), Decimal("-132")]
    )
    assert result.status == "multiple_roots"
    assert result.value is None
    roots = result.diagnostics["roots"]
    assert roots[0] == pytest.approx(Decimal("0.10"), abs=Decimal("1e-8"))
    assert roots[1] == pytest.approx(Decimal("0.20"), abs=Decimal("1e-8"))


def test_irr_root_at_zero_is_reported():
    result = internal_rate_of_return([Decimal("-100"), Decimal("100")])
    assert result.status == "unique_root"
    assert result.value == Decimal("0")


def test_irr_negative_but_admissible_root_is_reported():
    result = internal_rate_of_return([Decimal("-100"), Decimal("90")])
    assert result.status == "unique_root"
    assert result.value == pytest.approx(Decimal("-0.10"), abs=Decimal("1e-9"))


def test_irr_no_economically_valid_root_is_explicit():
    result = internal_rate_of_return(
        [Decimal("-100"), Decimal("10"), Decimal("-100")]
    )
    assert result.status == "no_root"
    assert result.value is None


def test_irr_is_invariant_to_positive_cash_flow_scaling():
    cash_flows = [Decimal("-100"), Decimal("0"), Decimal("121")]
    scaled = [value * Decimal("1000000") for value in cash_flows]
    base = internal_rate_of_return(cash_flows)
    result = internal_rate_of_return(scaled)
    assert result.status == "unique_root"
    assert result.value == pytest.approx(base.value, abs=Decimal("1e-9"))


def test_irr_returned_root_has_residual_within_recorded_tolerance():
    cash_flows = [Decimal("-100"), Decimal("0"), Decimal("121")]
    result = internal_rate_of_return(cash_flows)
    assert result.value is not None
    residual = abs(periodic_npv(cash_flows, result.value))
    assert residual <= result.diagnostics["residual_tolerance"]


# Payback policy


def test_simple_payback_exact_period_boundary():
    result = simple_payback([Decimal("-100"), Decimal("40"), Decimal("60")])
    assert result.status == "exact"
    assert result.value == Decimal("2")


def test_simple_payback_interpolates_first_crossing():
    result = simple_payback([Decimal("-100"), Decimal("60"), Decimal("60")])
    assert result.status == "interpolated"
    assert result.value == Decimal("1") + Decimal("40") / Decimal("60")


def test_simple_payback_zero_only_when_non_negative_at_inception():
    result = simple_payback([Decimal("0"), Decimal("-10")])
    assert result.status == "exact"
    assert result.value == Decimal("0")


def test_simple_payback_absent_recovery_is_explicit():
    result = simple_payback([Decimal("-100"), Decimal("20"), Decimal("20")])
    assert result.status == "no_payback"
    assert result.value is None


def test_simple_payback_rejects_empty_cash_flows():
    result = simple_payback([])
    assert result.status == "invalid_cashflows"
    assert result.value is None


def test_discounted_payback_interpolates_discounted_flows():
    result = discounted_payback(
        [Decimal("-100"), Decimal("60"), Decimal("60")],
        Decimal("0.10"),
        cash_flow_basis="real",
        discount_rate_basis="real",
    )
    assert result.status == "interpolated"
    assert result.value == pytest.approx(Decimal("1.9166666667"), abs=Decimal("1e-9"))
    assert result.discount_rate == Decimal("0.10")


def test_simple_payback_can_exist_without_discounted_payback():
    cash_flows = [Decimal("-100"), Decimal("60"), Decimal("40")]
    assert simple_payback(cash_flows).status == "exact"
    discounted = discounted_payback(
        cash_flows,
        Decimal("0.10"),
        cash_flow_basis="real",
        discount_rate_basis="real",
    )
    assert discounted.status == "no_discounted_payback"
    assert discounted.value is None


def test_discounted_payback_rejects_basis_mismatch_and_invalid_rate():
    mismatch = discounted_payback(
        [Decimal("-100"), Decimal("120")],
        Decimal("0.10"),
        cash_flow_basis="real",
        discount_rate_basis="nominal",
    )
    assert mismatch.status == "invalid_cashflows"
    invalid_rate = discounted_payback(
        [Decimal("-100"), Decimal("120")],
        Decimal("-1"),
        cash_flow_basis="real",
        discount_rate_basis="real",
    )
    assert invalid_rate.status == "invalid_cashflows"


# LLCR policy


def test_llcr_level_principal_matches_hand_calculation():
    rows = debt_schedule(debt_component("level_principal"))
    result = loan_life_coverage_ratio(
        {1: Decimal("50"), 2: Decimal("50"), 3: Decimal("50")},
        rows,
        Decimal("0.10"),
        cads_basis="real",
        debt_discount_rate_basis="real",
    )
    expected_initial = (
        Decimal("50")
        + Decimal("50") / Decimal("1.1")
        + Decimal("50") / (Decimal("1.1") ** 2)
    ) / Decimal("90")
    assert result.status == "calculated"
    assert result.initial_llcr == expected_initial
    assert result.minimum_llcr == expected_initial


def test_llcr_calculates_for_annuity_and_bullet_debt():
    for profile in ("annuity", "bullet"):
        rows = debt_schedule(debt_component(profile))
        result = loan_life_coverage_ratio(
            {1: Decimal("50"), 2: Decimal("50"), 3: Decimal("50")},
            rows,
            Decimal("0.08"),
            cads_basis="real",
            debt_discount_rate_basis="real",
        )
        assert result.status == "calculated"
        assert len(result.period_values) == 3


def test_llcr_is_not_applicable_without_debt_or_after_repayment():
    no_debt = loan_life_coverage_ratio(
        {},
        [],
        Decimal("0.08"),
        cads_basis="real",
        debt_discount_rate_basis="real",
    )
    assert no_debt.status == "not_applicable"
    repaid = loan_life_coverage_ratio(
        {},
        [
            DebtScheduleYear(
                year=4,
                opening_balance=Decimal("0"),
                interest=Decimal("0"),
                principal=Decimal("0"),
                debt_service=Decimal("0"),
                closing_balance=Decimal("0"),
            )
        ],
        Decimal("0.08"),
        cads_basis="real",
        debt_discount_rate_basis="real",
    )
    assert repaid.status == "not_applicable"


def test_llcr_negative_cfads_reduces_numerator():
    rows = debt_schedule(debt_component("level_principal"))
    positive = loan_life_coverage_ratio(
        {1: Decimal("50"), 2: Decimal("10"), 3: Decimal("50")},
        rows,
        Decimal("0.10"),
        cads_basis="real",
        debt_discount_rate_basis="real",
    )
    negative = loan_life_coverage_ratio(
        {1: Decimal("50"), 2: Decimal("-10"), 3: Decimal("50")},
        rows,
        Decimal("0.10"),
        cads_basis="real",
        debt_discount_rate_basis="real",
    )
    assert negative.initial_llcr < positive.initial_llcr


def test_llcr_excludes_cfads_after_debt_maturity():
    rows = debt_schedule(debt_component("level_principal"))
    base = loan_life_coverage_ratio(
        {1: Decimal("50"), 2: Decimal("50"), 3: Decimal("50")},
        rows,
        Decimal("0.10"),
        cads_basis="real",
        debt_discount_rate_basis="real",
    )
    extended = loan_life_coverage_ratio(
        {
            1: Decimal("50"),
            2: Decimal("50"),
            3: Decimal("50"),
            4: Decimal("1000000"),
        },
        rows,
        Decimal("0.10"),
        cads_basis="real",
        debt_discount_rate_basis="real",
    )
    assert extended.initial_llcr == base.initial_llcr
    assert extended.diagnostics["ignored_post_maturity_cfads_periods"] == [4]


def test_llcr_identifies_minimum_and_uses_opening_debt_balance():
    rows = debt_schedule(debt_component("level_principal"))
    result = loan_life_coverage_ratio(
        {1: Decimal("100"), 2: Decimal("20"), 3: Decimal("10")},
        rows,
        Decimal("0.10"),
        cads_basis="real",
        debt_discount_rate_basis="real",
    )
    final = result.period_values[-1]
    assert final.period == 3
    assert final.value == Decimal("10") / Decimal("30")
    assert result.minimum_llcr == final.value
    assert result.diagnostics["denominator"] == "opening_debt_balance"


def test_llcr_rejects_basis_mismatch_or_missing_loan_life_cfads():
    rows = debt_schedule(debt_component("level_principal"))
    mismatch = loan_life_coverage_ratio(
        {1: Decimal("50"), 2: Decimal("50"), 3: Decimal("50")},
        rows,
        Decimal("0.10"),
        cads_basis="real",
        debt_discount_rate_basis="nominal",
    )
    assert mismatch.status == "invalid_inputs"
    missing = loan_life_coverage_ratio(
        {1: Decimal("50"), 3: Decimal("50")},
        rows,
        Decimal("0.10"),
        cads_basis="real",
        debt_discount_rate_basis="real",
    )
    assert missing.status == "invalid_inputs"
    assert missing.diagnostics["missing_periods"] == [2]
