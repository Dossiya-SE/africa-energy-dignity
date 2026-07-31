# FIN-001 Canonical Finance Data Contract

- Document ID: `AED-FIN-CONTRACT-001`
- Version: `1.0.0`
- Status: Frozen implementation baseline
- Issue: `FIN-001 / #22`
- Schema: `schemas/finance.schema.json`
- Formula specification: `docs/finance/fin-001-mathematical-specification.md`

## 1. Purpose

This contract defines the minimum information required to calculate, reproduce, audit and compare AED project-finance, lifecycle-cost and affordability results.

The contract is deliberately stricter than a spreadsheet. A value is not calculation-ready merely because it is numeric. Every material monetary assumption must identify its currency, price year, real or nominal basis, evidence state and limitations.

## 2. Canonical scenario identity

Every calculation belongs to one immutable scenario version identified by:

```text
scenario_id
scenario_version
formula_version
geography_id
project_id, when the scenario represents a real registered project
is_synthetic
responsible_contributor
created_at
updated_at
```

A recalculation after any material input change requires a new scenario version or a new calculation-run identity. Existing results must not be silently overwritten.

## 3. Monetary convention

Every monetary quantity is represented as:

```json
{
  "amount": 1000000,
  "currency": "XOF",
  "price_year": 2026,
  "basis": "real"
}
```

### 3.1 Required controls

- Currency uses an uppercase three-letter ISO-style code.
- Price year is mandatory.
- Basis is exactly `real` or `nominal`.
- Monetary quantities cannot be added unless currency, price year and basis are compatible.
- Currency conversion requires an explicit transformation record containing the exchange rate, rate date or model period, source, method and output currency.
- Price-year conversion requires an explicit inflation or deflator transformation.
- Real-to-nominal or nominal-to-real conversion requires an explicit inflation convention.

No implicit conversion is permitted.

## 4. Discount-rate convention

A scenario declares:

```text
discount_rate
discount_rate_basis
inflation_rate, required for nominal scenarios
```

All rates are decimals:

```text
8% = 0.08
```

A real monetary scenario requires a real discount rate. A nominal monetary scenario requires a nominal discount rate and an explicit inflation rate. Mixed conventions are invalid.

## 5. Project horizon

The project timeline uses integer year offsets:

```text
year 0 = valuation and initial-investment date
year 1..T = operating or subsequent lifecycle years
```

Required fields:

```text
project_start_year
project_lifetime_years
construction_years
```

`project_lifetime_years` must be strictly positive. Cost or replacement events outside the lifecycle horizon are excluded from calculation and reported as validation warnings or errors according to the event type.

## 6. Cost items

Cost categories are:

```text
capex
fixed_opex
variable_opex
fuel
replacement
tax
duty
decommissioning
salvage_value
```

Each item includes:

```text
cost_id
category
timing_year
value
quantity_driver, where applicable
quantity_unit, where applicable
evidence
```

`salvage_value` is a positive input that enters project cost cash flow with a negative sign at its timing year. No other cost category changes sign implicitly.

## 7. Energy delivery

Annual energy is represented by year, non-negative quantity, unit and evidence.

Permitted units in FIN-001 are:

```text
kWh
MWh
GWh
```

All energy quantities are converted deterministically to the scenario calculation unit before aggregation. LCOE is undefined when discounted lifecycle energy is zero.

## 8. Financing components

Permitted financing types are:

```text
debt
equity
grant
subsidy
```

Every component contains an amount and evidence. Debt additionally requires:

```text
interest_rate
tenor_years
grace_period_years
repayment_profile
```

Permitted initial repayment profiles are:

```text
level_principal
annuity
bullet
custom
```

FIN-001 must verify that financing components reconcile to the declared financing requirement within a documented absolute and relative tolerance. Debt principal may never become negative.

## 9. Customer and affordability contract

Each customer class preserves its own identity and assumptions:

```text
customer_class_id
name
customer_count
annual_consumption_per_customer
energy_unit
tariff_per_energy
monthly_fixed_charge
monthly_disposable_income
connection_charge
evidence
```

Affordability indicators are calculated per customer class. Monthly disposable income must be strictly positive whenever an affordability ratio is requested.

WorldPop population evidence may support population or spatial aggregation. It does not establish household income, demand, willingness to pay or connection probability.

## 10. Evidence lineage

Every material assumption contains:

```text
source_id, required for observed or published evidence
evidence_class
validation_status
responsible_contributor
limitations
uncertainty, when available
```

Evidence classes and validation states use the approved AED canonical enumerations.

Synthetic fixtures use `scenario` or `assumed` evidence and must remain visibly synthetic in the API and interface.

## 11. Result contract

Every calculated result must carry:

```text
indicator_id
indicator_name
value
unit
currency, when monetary
price_year, when monetary
basis, when monetary
formula_version
scenario_id
scenario_version
calculation_run_id
input_hash
calculated_at
warnings
evidence_lineage
```

Undefined results are represented explicitly with a reason. They must not be converted to zero, infinity or a fabricated fallback value.

## 12. Required deterministic indicators

FIN-001 includes:

```text
net_present_cost
discounted_lifecycle_energy
lcoe
npv
irr
simple_payback
discounted_payback
break_even_tariff
required_subsidy
dscr_by_year
minimum_dscr
llcr, when defined
household_energy_burden
connection_cost_burden
productive_use_affordability
```

## 13. Validation order

The engine validates in this sequence:

1. schema and identifiers;
2. evidence and synthetic-status controls;
3. monetary compatibility;
4. temporal horizon;
5. energy units and non-negativity;
6. financing reconciliation;
7. debt terms;
8. affordability denominators;
9. formula preconditions;
10. result lineage and reproducibility.

No calculation may bypass a failed blocking validation.

## 14. Exclusions

This frozen contract does not include:

- procurement or supplier scoring;
- payment processing;
- credit scoring;
- political evaluation;
- energy-system optimization;
- stochastic Monte Carlo execution;
- automated investment recommendations;
- unsupported real-project claims.

## 15. Change control

Changes to required fields, enumerations, monetary conventions, formula semantics or evidence gates require:

1. a version increment;
2. an issue explaining compatibility impact;
3. updated schema examples;
4. updated mathematical specification;
5. migration and regression tests where persistence is affected.
