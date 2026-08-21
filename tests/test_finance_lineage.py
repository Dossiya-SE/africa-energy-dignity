"""Deterministic canonical hashing and result-lineage tests for FIN-001."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json

import pytest

from aed.finance.lineage import (
    attach_indicator_lineage,
    build_calculation_run_identity,
    canonical_json_bytes,
    canonical_scenario_bytes,
    scenario_input_hash,
)
from aed.finance.models import (
    CostItem,
    EnergyYear,
    EvidenceReference,
    FinanceScenario,
    FinancingComponent,
    IRRResult,
    Money,
)


def evidence(limitation: str = "Synthetic deterministic fixture.") -> EvidenceReference:
    return EvidenceReference(
        evidence_class="scenario",
        validation_status="schema_valid",
        responsible_contributor="Synthetic AED reviewer",
        limitations=[limitation],
    )


def money(amount: str) -> Money:
    return Money(
        amount=Decimal(amount),
        currency="XOF",
        price_year=2026,
        basis="real",
    )


def scenario(
    *,
    capex: str = "100.00",
    created_at: datetime | None = None,
    limitation: str = "Synthetic deterministic fixture.",
) -> FinanceScenario:
    timestamp = created_at or datetime(2026, 7, 31, tzinfo=timezone.utc)
    return FinanceScenario(
        scenario_id="finance.scenario.synthetic.lineage.v1",
        name="Synthetic lineage fixture",
        scenario_version="1.0.0",
        formula_version="FIN-001.1",
        geography_id="geo.bfa",
        is_synthetic=True,
        reporting_currency="XOF",
        price_year=2026,
        monetary_basis="real",
        discount_rate=Decimal("0.08"),
        discount_rate_basis="real",
        funding_requirement=money("100"),
        project_start_year=2026,
        project_lifetime_years=2,
        construction_years=0,
        cost_items=[
            CostItem(
                cost_id="cost.synthetic.capex",
                category="capex",
                timing_year=0,
                value=money(capex),
                evidence=evidence(limitation),
            )
        ],
        annual_energy=[
            EnergyYear(
                year=1,
                energy=Decimal("10.0"),
                unit="MWh",
                evidence=evidence(),
            ),
            EnergyYear(
                year=2,
                energy=Decimal("10.00"),
                unit="MWh",
                evidence=evidence(),
            ),
        ],
        financing_components=[
            FinancingComponent(
                component_id="finance.synthetic.equity",
                type="equity",
                amount=money("100.0"),
                evidence=evidence(),
            )
        ],
        customer_classes=[],
        validation_status="schema_valid",
        responsible_contributor="Synthetic AED reviewer",
        created_at=timestamp,
        updated_at=timestamp,
    )


def test_canonical_json_is_independent_of_mapping_insertion_order():
    left = {"b": Decimal("2.00"), "a": Decimal("1.0")}
    right = {"a": Decimal("1.00"), "b": Decimal("2")}
    assert canonical_json_bytes(left) == canonical_json_bytes(right)
    assert json.loads(canonical_json_bytes(left))["a"] == {"$decimal": "1"}


def test_equivalent_decimal_encodings_produce_same_scenario_hash():
    assert scenario_input_hash(scenario(capex="100.00")) == scenario_input_hash(
        scenario(capex="100.0000")
    )


def test_timezone_equivalent_timestamps_produce_same_hash():
    utc = datetime(2026, 7, 31, 4, 0, tzinfo=timezone.utc)
    offset = utc.astimezone(timezone(timedelta(hours=8)))
    assert scenario_input_hash(scenario(created_at=utc)) == scenario_input_hash(
        scenario(created_at=offset)
    )


def test_material_input_or_evidence_change_changes_hash():
    base = scenario_input_hash(scenario())
    assert scenario_input_hash(scenario(capex="101")) != base
    assert scenario_input_hash(scenario(limitation="Different limitation.")) != base


def test_canonical_scenario_bytes_are_stable_and_sha256_labelled():
    fixture = scenario()
    assert canonical_scenario_bytes(fixture) == canonical_scenario_bytes(fixture)
    digest = scenario_input_hash(fixture)
    assert digest.startswith("sha256:")
    assert len(digest) == len("sha256:") + 64


def test_calculation_run_identity_is_content_addressed_and_repeatable():
    fixture = scenario()
    first = build_calculation_run_identity(fixture, software_version="0.1.0")
    second = build_calculation_run_identity(fixture, software_version="0.1.0")
    assert first == second
    assert first.input_hash == scenario_input_hash(fixture)
    assert first.calculation_run_id.startswith("finance.run.sha256.")


def test_software_version_changes_run_identity_material():
    fixture = scenario()
    baseline = build_calculation_run_identity(fixture, software_version="0.1.0")
    changed_software = build_calculation_run_identity(
        fixture,
        software_version="0.1.1",
    )
    assert changed_software.calculation_run_id != baseline.calculation_run_id

    assert baseline.formula_version == fixture.formula_version


def test_indicator_lineage_attaches_without_changing_indicator_result():
    identity = build_calculation_run_identity(scenario(), software_version="0.1.0")
    result = IRRResult(
        value=Decimal("0.1"),
        status="unique_root",
        method="deterministic_bracketed_solver",
        tolerance=Decimal("1e-10"),
        iterations=20,
    )
    lineaged = attach_indicator_lineage(
        result,
        identity,
        indicator_name="irr",
    )
    assert lineaged.value == result.value
    assert lineaged.status == result.status
    assert lineaged.lineage is not None
    assert lineaged.lineage.indicator_name == "irr"
    assert lineaged.lineage.calculation_run_id == identity.calculation_run_id


def test_lineage_rejects_formula_mismatch_and_empty_versions():
    fixture = scenario()
    with pytest.raises(ValueError, match="software_version"):
        build_calculation_run_identity(fixture, software_version="  ")

    identity = build_calculation_run_identity(fixture, software_version="0.1.0")
    result = IRRResult(
        value=Decimal("0.1"),
        status="unique_root",
        method="deterministic_bracketed_solver",
        formula_version="FIN-001.1",
        tolerance=Decimal("1e-10"),
        iterations=20,
    )
    tampered = identity.model_copy(update={"formula_version": "FIN-999"})
    with pytest.raises(ValueError, match="formula versions"):
        attach_indicator_lineage(result, tampered, indicator_name="irr")
