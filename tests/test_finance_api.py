"""Regression tests for the transparent FIN-001 finance API."""
from __future__ import annotations

import json

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from aed.database.models import (
    FinanceCalculationExecution,
    FinanceIndicatorResultRecord,
    Geography,
)
from scripts.seed_finance import DEFAULT_FIXTURE


def _scenario_payload() -> dict:
    return json.loads(DEFAULT_FIXTURE.read_text(encoding="utf-8"))


def _add_burkina_geography(db: Session) -> None:
    if db.get(Geography, "geo.bfa") is None:
        db.add(
            Geography(
                id="geo.bfa",
                name="Burkina Faso",
                level="country",
                iso_code="BFA",
                geometry_status="validated",
            )
        )
        db.commit()


def _create_scenario(client: TestClient, db: Session) -> dict:
    _add_burkina_geography(db)
    response = client.post("/finance/scenarios", json=_scenario_payload())
    assert response.status_code == 201
    return response.json()


def test_scenario_create_get_list_and_idempotency(
    client: TestClient,
    db_session: Session,
):
    created = _create_scenario(client, db_session)
    repeated = client.post("/finance/scenarios", json=_scenario_payload())

    assert repeated.status_code == 200
    assert repeated.json()["scenario_record_id"] == created["scenario_record_id"]
    assert repeated.json()["input_hash"] == created["input_hash"]
    assert created["is_synthetic"] is True
    assert created["scenario"]["is_synthetic"] is True

    fetched = client.get(
        f"/finance/scenarios/{created['scenario_record_id']}"
    )
    assert fetched.status_code == 200
    assert fetched.json()["input_hash"] == created["input_hash"]

    listed = client.get("/finance/scenarios?limit=10&offset=0")
    assert listed.status_code == 200
    assert listed.json()["items"][0]["scenario_record_id"] == (
        created["scenario_record_id"]
    )


def test_same_scenario_version_with_changed_content_returns_conflict(
    client: TestClient,
    db_session: Session,
):
    _create_scenario(client, db_session)
    changed = _scenario_payload()
    changed["discount_rate"] = "0.09"

    response = client.post("/finance/scenarios", json=changed)

    assert response.status_code == 409
    assert "different canonical content" in response.json()["detail"]


def test_scenario_requires_existing_geography(client: TestClient):
    payload = _scenario_payload()
    payload["geography_id"] = "geo.missing"

    response = client.post("/finance/scenarios", json=payload)

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Finance scenario geography does not exist."
    )


def test_invalid_monetary_basis_is_rejected_by_request_validation(
    client: TestClient,
    db_session: Session,
):
    _add_burkina_geography(db_session)
    payload = _scenario_payload()
    payload["discount_rate_basis"] = "nominal"

    response = client.post("/finance/scenarios", json=payload)

    assert response.status_code == 422


def test_repeated_calculations_share_run_identity_but_not_execution(
    client: TestClient,
    db_session: Session,
):
    scenario = _create_scenario(client, db_session)
    request = {"scenario_record_id": scenario["scenario_record_id"]}

    first = client.post("/finance/calculations", json=request)
    second = client.post("/finance/calculations", json=request)

    assert first.status_code == 201
    assert second.status_code == 201
    first_payload = first.json()
    second_payload = second.json()
    assert first_payload["calculation_run_id"] == second_payload[
        "calculation_run_id"
    ]
    assert first_payload["input_hash"] == second_payload["input_hash"]
    assert first_payload["execution_id"] != second_payload["execution_id"]
    assert first_payload["indicator_count"] == 13
    assert second_payload["indicator_count"] == 13

    count = db_session.scalar(
        select(func.count()).select_from(FinanceCalculationExecution)
    )
    assert count == 2


def test_execution_cash_flow_indicators_affordability_and_validations(
    client: TestClient,
    db_session: Session,
):
    scenario = _create_scenario(client, db_session)
    calculation = client.post(
        "/finance/calculations",
        json={"scenario_record_id": scenario["scenario_record_id"]},
    )
    assert calculation.status_code == 201
    execution = calculation.json()
    execution_id = execution["execution_id"]

    fetched = client.get(f"/finance/executions/{execution_id}")
    assert fetched.status_code == 200
    assert fetched.json()["status"] == "succeeded"
    assert fetched.json()["is_synthetic"] is True

    cash_flow = client.get(
        f"/finance/executions/{execution_id}/cash-flow"
    )
    assert cash_flow.status_code == 200
    cash_payload = cash_flow.json()
    assert len(cash_payload["rows"]) == 11
    assert cash_payload["rows"][0]["year"] == 0
    assert isinstance(cash_payload["rows"][0]["net_cash_flow"], str)
    assert cash_payload["calculation_run_id"] == execution[
        "calculation_run_id"
    ]

    indicators = client.get(
        f"/finance/executions/{execution_id}/indicators"
    )
    assert indicators.status_code == 200
    indicator_items = indicators.json()["items"]
    names = [item["indicator_name"] for item in indicator_items]
    assert names == sorted(names)
    assert len(indicator_items) == 11
    assert {"lcoe", "npv", "irr"}.issubset(names)
    lcoe_result = next(
        item for item in indicator_items if item["indicator_name"] == "lcoe"
    )
    assert isinstance(lcoe_result["result"]["value"], str)
    assert lcoe_result["lineage"]["calculation_run_id"] == execution[
        "calculation_run_id"
    ]

    affordability = client.get(
        f"/finance/executions/{execution_id}/affordability"
    )
    assert affordability.status_code == 200
    affordability_items = affordability.json()["items"]
    assert len(affordability_items) == 2
    assert all(
        item["indicator_name"].startswith("affordability.")
        for item in affordability_items
    )
    assert all(
        isinstance(item["result"]["monthly_bill"], str)
        for item in affordability_items
    )

    validations = client.get(
        f"/finance/scenarios/{scenario['scenario_record_id']}/validations"
    )
    assert validations.status_code == 200
    validation_items = validations.json()["items"]
    assert len(validation_items) == 1
    assert validation_items[0]["status"] == "warning"
    assert validation_items[0]["checks"]["is_synthetic"] is True


def test_failed_calculation_records_terminal_execution(
    client: TestClient,
    db_session: Session,
):
    _add_burkina_geography(db_session)
    payload = _scenario_payload()
    payload["scenario_id"] = "finance.scenario.synthetic.bfa.zero_energy.v1"
    payload["name"] = "Synthetic zero-energy calculation failure scenario"
    for year in payload["annual_energy"]:
        year["energy"] = "0"

    created = client.post("/finance/scenarios", json=payload)
    assert created.status_code == 201
    scenario_record_id = created.json()["scenario_record_id"]

    response = client.post(
        "/finance/calculations",
        json={"scenario_record_id": scenario_record_id},
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert "LCOE is undefined" in detail["message"]
    execution_id = detail["execution_id"]

    execution = client.get(f"/finance/executions/{execution_id}")
    assert execution.status_code == 200
    assert execution.json()["status"] == "failed"
    assert execution.json()["indicator_count"] == 0

    stored_results = db_session.scalar(
        select(func.count())
        .select_from(FinanceIndicatorResultRecord)
        .where(FinanceIndicatorResultRecord.execution_id == execution_id)
    )
    assert stored_results == 0

    validations = client.get(
        f"/finance/scenarios/{scenario_record_id}/validations"
    )
    assert validations.status_code == 200
    assert validations.json()["items"][0]["status"] == "failed"


def test_finance_not_found_and_pagination_controls(client: TestClient):
    assert client.get("/finance/scenarios/missing").status_code == 404
    assert client.get("/finance/executions/missing").status_code == 404
    assert client.get("/finance/scenarios?limit=101").status_code == 422
    assert client.get("/finance/scenarios?offset=-1").status_code == 422


def test_finance_records_have_no_mutating_routes(
    client: TestClient,
    db_session: Session,
):
    scenario = _create_scenario(client, db_session)
    path = f"/finance/scenarios/{scenario['scenario_record_id']}"

    assert client.put(path, json={}).status_code == 405
    assert client.patch(path, json={}).status_code == 405
    assert client.delete(path).status_code == 405
