# Africa Energy Dignity

## Open Energy Sovereignty Modeling and Rapid Deployment Engineering for Sub-Saharan Africa

[![AED application](https://github.com/Dossiya-SE/africa-energy-dignity/actions/workflows/python-app.yml/badge.svg)](https://github.com/Dossiya-SE/africa-energy-dignity/actions/workflows/python-app.yml)
![stage](https://img.shields.io/badge/stage-pre--alpha-orange)

<p align="center"><img src="docs/assets/aed-mathematical-system.svg" width="100%" alt="AED evidence, energy physics, resilience, optimization and deployment architecture" /></p>

> **Electricity access is an input. Productive capability, critical-service continuity, resilience and energy sovereignty are the system outcomes.**

## Mathematical engineering core

Energy balance:

```math
P_{gen}+P_{import}+P_{dis}=P_{load}+P_{loss}+P_{ch}+P_{export}.
```

Coupled resilience model class:

```math
\dot x=f(x,u,\eta;\theta),\qquad S(t)=w^Tx(t).
```

Multi-objective design principle:

```math
\min_d [C(d),E(d),T(d),Risk(d)],
\qquad
\max_d [Service(d),Resilience(d),Sovereignty(d)].
```

A rapid-deployment clock can be decomposed as

```math
T_{impact}=T_{diagnosis}+T_{design}+T_{approval}+T_{finance}+T_{procurement}+T_{construction}+T_{commissioning}.
```

The optimization objective is **not** minimum time alone; reliability, affordability, safety, maintainability, environmental constraints and local capability remain admissibility conditions.

## What exists today

| Implemented evidence | Verification |
|---|---|
| canonical schemas + data contracts | schema validators |
| PostgreSQL/PostGIS + Alembic migrations | CI migration against PostGIS |
| geospatial/evidence registries | repository + geospatial validation |
| Python backend/API foundation | imports + compile + pytest |
| web application foundation | lint + typecheck + tests + build |
| governance, authorship, citation metadata | committed control documents |
| provenance/licensing rules | controlled registers |

**Not yet claimed:** production continental optimizer, validated investment recommendations, field deployment, causal productive-impact results, continent-wide coverage.

## Evidence flow

`source → provenance → canonical variable → model input → derived/model result → uncertainty/sensitivity → validation → decision`

Every major value should be distinguishable as **observed**, **official/published**, **derived**, **model output**, **expert judgment**, **scenario**, **design target**, or **planned**.

## Verification ≠ validation

```bash
make install
make lint
make validate
make test
make web-install
make web-lint
make web-typecheck
make web-test
make web-build
```

These commands establish repository/software consistency. Real-world model validity requires calibrated data, external/out-of-sample checks and explicit uncertainty analysis.

## Systems-engineering reference

AED uses **ISO/IEC/IEEE 15288:2023** as a life-cycle process reference and **W3C PROV-O** as a future provenance-interoperability reference. Neither reference is presented as certification.

## Technical entry points

[`docs/mathematical-framework.md`](docs/mathematical-framework.md) · [`docs/verification-validation.md`](docs/verification-validation.md) · [`docs/scientific-foundation.md`](docs/scientific-foundation.md) · [`PROJECT_SETUP.md`](PROJECT_SETUP.md) · [`GOVERNANCE.md`](GOVERNANCE.md) · [`CONTRIBUTING.md`](CONTRIBUTING.md)

## Project leadership

**Founder and Lead Systems Engineer:** [Dossiya Dakou](https://github.com/Dossiya-SE) · **ORCID:** [0009-0004-1071-9948](https://orcid.org/0009-0004-1071-9948)

> **Evidence → physics → optimization → engineering → deployment → measured productive capability.**
