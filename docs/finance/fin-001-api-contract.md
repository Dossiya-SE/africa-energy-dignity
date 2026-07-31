# FIN-001 transparent finance API contract

## Purpose

The FIN-001 API exposes validated finance scenarios, deterministic calculations,
immutable execution events, exact cash-flow series, indicators, affordability
results and validation evidence. It does not perform procurement, payment,
credit scoring, investment solicitation or real-project certification.

All finance records remain append-only. The API provides no `PUT`, `PATCH` or
`DELETE` route for finance scenarios, executions, results or validations.

## Endpoints

```text
GET  /finance/scenarios
GET  /finance/scenarios/{scenario_record_id}
POST /finance/scenarios
POST /finance/calculations
GET  /finance/executions/{execution_id}
GET  /finance/executions/{execution_id}/cash-flow
GET  /finance/executions/{execution_id}/indicators
GET  /finance/executions/{execution_id}/affordability
GET  /finance/scenarios/{scenario_record_id}/validations
```

List endpoints accept `limit` and `offset`. The limit is constrained to the
inclusive range 1–100. Results use deterministic database ordering before
pagination.

## Scenario creation

`POST /finance/scenarios` accepts the canonical `FinanceScenario` contract.
Pydantic validation runs before persistence. The route also requires referenced
geography and project records to exist.

An identical scenario ID and version is idempotent and returns the existing
record. A material change under an existing scenario ID and version returns
`409 Conflict`. A material change requires a new scenario version.

Every scenario response includes:

```text
scenario_record_id
scenario_id
scenario_version
formula_version
canonicalization_version
input_hash
geography_id
project_id
is_synthetic
currency, price year and monetary basis
validation status
canonical scenario payload
```

## Calculation identity and execution identity

The API software version is fixed in code as:

```text
AED-FIN-001-API-1
```

For the same canonical scenario, formula version, canonicalization version and
software version:

```text
same input_hash
same calculation_run_id
```

Each `POST /finance/calculations` request creates a distinct immutable execution
event:

```text
same calculation_run_id
new execution_id
```

The controlled seed script is intentionally different: it returns its existing
successful execution when repeated against the same database.

## Calculation scope

The API execution records:

- lifecycle net present cost;
- discounted energy;
- LCOE;
- project NPV before financing;
- break-even tariff;
- required year-zero subsidy baseline;
- IRR;
- simple and discounted payback;
- DSCR and LLCR for each debt component;
- affordability metrics for each customer class.

The current DSCR and LLCR API baseline uses pre-financing project cash flow as
the declared CFADS proxy because FIN-001.1 does not yet contain a separate tax,
reserve-account and working-capital CFADS schedule. That policy is preserved in
result diagnostics and must not be interpreted as a lender-grade model.

## Exact numeric serialization

Finance calculations use `Decimal`. Public JSON represents decimal values as
strings, never binary floating-point numbers. Every persisted result includes:

```text
input_hash
calculation_run_id
formula_version
canonicalization_version
software_version
indicator_name
method
status
warnings
calculation diagnostics
```

## Synthetic safeguards

Synthetic status is returned in scenario, execution and cash-flow responses.
The controlled Burkina Faso fixture remains visibly synthetic even after every
schema, calculation, persistence and API test passes.

Synthetic output must not be represented as:

- verified Burkina Faso project evidence;
- an investment recommendation;
- an approved tariff;
- a lender offer;
- a procurement estimate;
- a real affordability or subsidy claim.

## Error policy

```text
404  scenario or execution does not exist
409  immutable identity conflict or missing referenced registry record
422  malformed scenario, incompatible monetary basis or rejected calculation
405  unsupported mutation method
```

When a deterministic calculation is rejected after scenario validation, the API
first records a terminal failed execution and failed validation event. The `422`
response includes that immutable `execution_id` for audit inspection.
