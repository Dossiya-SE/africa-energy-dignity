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
    affordability_metrics,
    debt_schedule,
    dscr,
    lcoe,
    net_present_cost,
    npv,
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
    debt = FinancingComponent(
        component_id="finance.synthetic.debt",
        type="debt",
        amount=money("90"),
        interest_rate=Decimal("0.10"),
        tenor_years=3,
        grace_period_years=0,
        repayment_profile="level_principal",
        evidence=evidence(),
    )
    rows = debt_schedule(debt)
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
