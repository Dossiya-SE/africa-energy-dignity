# Africa Energy Dignity

## Open Energy Sovereignty Modeling and Rapid Deployment Engineering for Sub-Saharan Africa

[![AED application](https://github.com/Dossiya-SE/africa-energy-dignity/actions/workflows/python-app.yml/badge.svg)](https://github.com/Dossiya-SE/africa-energy-dignity/actions/workflows/python-app.yml)
[![Project stage](https://img.shields.io/badge/stage-pre--alpha-orange)](#development-status)
[![Development model](https://img.shields.io/badge/model-open%20science%20%2B%20open%20engineering-blue)](#operating-principles)

> **From electricity access to productive capability, infrastructure resilience and sovereign development.**

## Mission

**Africa Energy Dignity (AED)** is an open-source scientific, engineering and decision-support initiative for accelerating reliable, affordable, productive, resilient and locally governable energy systems across Sub-Saharan Africa.

The central proposition is:

> Electricity access is not the final objective. The objective is the expansion of human capability, productive activity, critical-service continuity, industrial capacity, infrastructure resilience and energy sovereignty.

## What is evidenced in this repository today

AED is intentionally explicit about maturity. The repository currently provides an **executable foundation**, not a completed continental energy-system optimizer.

| Evidence-bearing element | Repository evidence | Status |
|---|---|---|
| Canonical data architecture | versioned schemas, registry models, data contracts | implemented baseline |
| Database evolution | Alembic migrations + PostgreSQL/PostGIS CI service | executable |
| Repository validation | `scripts/validate_repository.py` | automated |
| Schema validation | `scripts/validate_schemas.py` | automated |
| Geospatial evidence validation | `scripts/validate_geospatial.py` | automated |
| Backend verification | import checks, compile checks, pytest | automated |
| Web verification | lint, type-check, tests, production build | automated |
| Governance / authorship | `GOVERNANCE.md`, `AUTHORS.md`, `CONTRIBUTING.md` | documented |
| Citation metadata | `CITATION.cff` | committed |
| Data-rights/provenance controls | data register + licensing rules | defined |
| Optimization results | no production results yet | **not completed** |
| Country-scale deployment claims | no operational deployment evidence yet | **not claimed** |

This distinction is intentional: **repository infrastructure is evidence of implementation; it is not evidence that future model outputs or deployments already exist.**

## Operating principles

1. Dignity is the objective.
2. Urgency is a formal design constraint.
3. Evidence precedes major decisions.
4. Speed must not compromise safety, reliability or maintainability.
5. Models must be transparent, reproducible and uncertainty-aware.
6. Productive demand must be planned before infrastructure is sized.
7. African realities must determine system assumptions.
8. Local capability must increase with every deployment.
9. Data sovereignty is part of energy sovereignty.
10. Every validated solution should become reusable institutional knowledge.

## Core delivery chain

```text
Evidence
→ Decision
→ Engineering
→ Finance
→ Procurement
→ Construction
→ Commissioning
→ Productive Impact
→ Monitoring / Learning
```

A rapidity metric may be written as

```text
T_impact = T_diagnosis + T_design + T_approval + T_finance
         + T_procurement + T_construction + T_commissioning
```

The engineering objective is not to minimize time alone, but to reduce `T_impact` while satisfying declared reliability, affordability, safety, environmental, local-capability and critical-service constraints.

## Systems-engineering structure

AED uses **ISO/IEC/IEEE 15288:2023** as a systems life-cycle process reference where useful for architecture and governance. This repository does **not** claim audited ISO compliance or certification.

The working life-cycle logic is:

```text
stakeholder need
→ evidence / context definition
→ requirements
→ architecture
→ analysis / trade study
→ implementation
→ integration
→ verification
→ validation
→ operation / monitoring
→ learning / revision
```

The standard is used as a process reference, not as a substitute for domain-specific engineering standards, national regulation or independent review.

## System architecture

| Layer | Purpose | Evidence gate |
|---|---|---|
| Baseline diagnosis | Establish demographic, infrastructure, demand, cost and hazard conditions | traceable source + provenance |
| Demand and capability modeling | Estimate observed, unserved, suppressed, productive and future demand | declared method + validation data |
| Technology modeling | Represent grid, mini-grid, stand-alone, generation, storage and efficiency options | parameter provenance + engineering constraints |
| Multi-objective optimization | Compare cost, speed, reliability, resilience, productive impact and sovereignty | solver formulation + sensitivity + reproducibility |
| Deployment engineering | Convert preferred scenarios into sequenced implementation packages | requirements + interfaces + risk controls |
| Monitoring and learning | Verify service outcomes and revise assumptions | observed post-deployment evidence |

## Evidence classes

Every major input or result should be classifiable as one of the following:

- **Observed data** — direct measurement or administrative record.
- **Published / official evidence** — peer-reviewed literature, government, regulator, standard or auditable institution.
- **Derived value** — computed from declared source variables and method.
- **Model output** — simulation/optimization result conditional on assumptions.
- **Expert judgment** — explicitly attributed professional judgment.
- **Scenario choice** — intentionally selected exploratory value.
- **Design target** — engineering requirement or provisional specification.
- **Planned** — work that has not yet been executed.

**No estimated, simulated or scenario value may be presented as measured evidence.**

## Provenance model

The repository treats provenance as part of engineering validity. The conceptual lineage is:

```text
source
→ acquisition record
→ raw / preserved evidence
→ transformation
→ canonical record
→ model input
→ derived result
→ decision artifact
```

W3C **PROV-O** is used as a reference model for future machine-readable provenance interoperability. Existing repository controls do not imply that every current object is already serialized as PROV-O.

## Verification and validation

AED separates **verification** from **validation**:

- **Verification:** did we implement the declared software/schema/process correctly?
- **Validation:** does the resulting model or system adequately represent the intended real-world use?

Current CI is primarily a **verification** layer.

### Backend CI checks

The `AED application` workflow currently executes:

- Python 3.11 environment setup;
- dependency installation;
- flake8 checks;
- repository-structure validation;
- canonical-schema validation;
- geospatial-evidence validation;
- import verification;
- Docker Compose configuration validation;
- Alembic migration against PostgreSQL/PostGIS;
- `pytest -q`;
- Python source compilation.

### Web CI checks

The web job executes:

- locked dependency installation with `npm ci`;
- lint;
- TypeScript type-checking;
- tests;
- production build.

### Local verification

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

Database / service operations:

```bash
make migrate
make seed
make up
make down
```

Passing these commands demonstrates software/repository consistency. It does **not** by itself validate an energy-system model against field observations.

## Model credibility gate

Before a model result is promoted to a decision claim, the intended chain is:

```text
source provenance
→ variable definition / units
→ model formulation
→ parameter provenance
→ calibration where required
→ numerical verification
→ sensitivity / uncertainty
→ out-of-sample or external validation
→ decision interpretation
```

If any link is absent, the limitation must be stated next to the result.

## Initial workstreams

- Scientific foundation and systematic evidence synthesis
- Data infrastructure and geospatial intelligence
- Mathematical energy-system modeling
- Productive-use and industrial-demand modeling
- Reliability and infrastructure resilience
- Rapid deployment and systems engineering
- Dashboard and decision-support platform
- Governance, local capability and energy sovereignty
- Country and community demonstration cases
- Verification, validation and open-source collaboration

## Development status

AED is in the **pre-alpha executable-foundation phase**.

The immediate mission is to establish and harden:

- governed source and institution registries;
- canonical geography and asset records;
- reproducible database migrations;
- tested backend/API behavior;
- controlled geospatial fixtures;
- append-only or auditable evidence events where applicable;
- a traceable transition from verified evidence to later modeling.

The current repository already contains the architecture, schemas, migrations, API/web foundation, governance and verification scaffolding needed for that phase.

The following should **not** be inferred as completed merely from the repository vision:

- production-scale data ingestion for all target countries;
- final energyRt implementation;
- final native Pyomo optimization model;
- validated investment recommendations;
- field-deployed infrastructure;
- validated causal claims about productive impact;
- continent-wide dashboard coverage.

## Repository map

```text
.
├── .github/                 workflows, issue forms and PR quality controls
├── alembic/                 versioned database migrations
├── config/                  controlled model/application configuration
├── data/                    data zones, fixtures, registers and provenance controls
├── docs/                    scientific, engineering and governance documentation
├── notebooks/               exploratory analyses only
├── scripts/                 reproducible validation / command-line workflows
├── src/aed/                 tested backend and registry/API source
├── tests/                   verification and regression tests
├── web/                     frontend / AED Studio
├── CITATION.cff             citation metadata
├── GOVERNANCE.md            authority and decision structure
└── Makefile                 reproducible project commands
```

## Documentation entry points

- [`docs/project-charter.md`](docs/project-charter.md)
- [`docs/scientific-foundation.md`](docs/scientific-foundation.md)
- [`docs/literature-review-protocol.md`](docs/literature-review-protocol.md)
- [`docs/mathematical-framework.md`](docs/mathematical-framework.md)
- [`docs/verification-validation.md`](docs/verification-validation.md)
- [`PROJECT_SETUP.md`](PROJECT_SETUP.md)
- [`GOVERNANCE.md`](GOVERNANCE.md)
- [`CONTRIBUTING.md`](CONTRIBUTING.md)

## Project leadership

**Founder and Lead Systems Engineer:** [Dossiya Dakou](https://github.com/Dossiya-SE)  
**ORCID:** [0009-0004-1071-9948](https://orcid.org/0009-0004-1071-9948)

Project leadership includes scientific direction, system architecture, engineering standards, mathematical-model strategy, verification requirements, scope control and release approval.

## Development transparency

AI-assisted tools may support research organization, documentation, code generation, testing and design exploration.

Accepted outputs remain subject to:

- human review;
- source verification;
- repository validation;
- engineering judgment;
- explicit approval.

AI systems are not treated as authors, accountable engineers or validation authorities.

## Data and rights policy

Software is released under the repository license. Third-party datasets remain subject to their original licenses and must be registered with source, rights and provenance information before use.

Do not treat the presence of a dataset filename or metadata record as evidence that redistribution rights have been established.

## Contributing

Read [`CONTRIBUTING.md`](CONTRIBUTING.md), [`GOVERNANCE.md`](GOVERNANCE.md) and [`AUTHORS.md`](AUTHORS.md) before submitting work.

---

**Energy access must become productive power. Productive power must become sovereign development — with every major claim traceable to evidence, assumptions, computation and validation status.**
