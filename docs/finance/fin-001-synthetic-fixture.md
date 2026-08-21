# FIN-001 controlled synthetic finance fixture

## Purpose

`bfa_synthetic_energy_project.json` is a deterministic software-verification
fixture for FIN-001. It is not a project proposal, feasibility study, investment
recommendation, lender model, tariff recommendation or representation of an
actual Burkina Faso energy project.

The fixture exists to exercise:

- canonical finance-scenario validation;
- funding reconciliation;
- lifecycle cash-flow construction;
- deterministic IRR and payback policies;
- scenario hashing and calculation-run identity;
- immutable scenario, execution, result and validation persistence;
- repeatable SQLite and PostgreSQL regression tests.

## Synthetic status

Every monetary value, technical quantity, customer count, tariff, income,
financing term and operating assumption is deliberately invented. Round values
were selected to make engineering review and hand calculation practical.

The fixture is controlled by these mandatory safeguards:

```text
is_synthetic = true
project_id = null
name contains "Synthetic"
geography_id = geo.bfa
evidence_class in {scenario, assumed}
source_id = null
limitations are required for every assumption
validation_status = schema_valid
```

`geo.bfa` identifies the country context only. It does not convert any synthetic
assumption into observed, published or verified Burkina Faso evidence.

## Stable identity

The scenario uses:

```text
scenario_id:              finance.scenario.synthetic.bfa.energy_project.v1
scenario_version:         1.0.0
formula_version:          FIN-001.1
canonicalization_version: FIN-CANONICAL-JSON-1
seed software version:    AED-FIN-001-SYNTHETIC-SEED-1
```

The scenario input hash and deterministic calculation-run ID are computed from
the canonical fixture at execution time. They are not manually copied into the
JSON file.

A material fixture change with the same `scenario_id` and `scenario_version`
must be rejected. A controlled material change requires a new
`scenario_version`.

## Seed behavior

Run migrations before seeding:

```bash
alembic upgrade head
python scripts/seed_finance.py
```

An explicit database can be supplied:

```bash
python scripts/seed_finance.py \
  --database-url sqlite+pysqlite:////tmp/aed-finance-seed.db
```

The first run:

1. verifies the synthetic controls;
2. creates `geo.bfa` only when absent;
3. persists the immutable scenario;
4. calculates deterministic IRR, simple payback and discounted payback;
5. attaches complete calculation lineage;
6. records one successful execution, its results and a warning validation event.

A repeated run against the same database returns the existing execution. It
does not duplicate the scenario, execution, indicator results or validation
event.

## Prohibited use

The fixture must not be:

- presented as measured or published project evidence;
- used to claim a real LCOE, IRR, tariff, subsidy or affordability result;
- cited as a Burkina Faso project cost benchmark;
- used for procurement, credit decisions or investment solicitation;
- promoted from synthetic status without replacing every assumption with
  governed evidence and completing independent review.

The fixture remains test evidence even when all validation and regression gates
pass.
