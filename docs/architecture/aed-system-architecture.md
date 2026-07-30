# Africa Energy Dignity System Architecture

**Document ID:** `AED-ARCH-001`  
**Version:** `0.1`
**Status:** Approved architecture baseline
**Issue:** `ARCH-001` / Issue #3  
**First demonstration country:** Burkina Faso

## 1. Purpose

This document defines the platform-independent architecture of **Africa Energy Dignity (AED)** before production data ingestion, model implementation, dashboard programming or country-level recommendations begin.

AED is an Africa-centered scientific, mathematical, physical, engineering and public-purpose system for converting energy evidence into reliable infrastructure, productive capability, resilience and sovereignty.

The architecture connects:

1. African geospatial and institutional evidence;
2. a canonical data system;
3. a conventional reference energy-system model;
4. an AED-specific mathematical research model;
5. independent cross-model verification;
6. deployment engineering;
7. a verified decision-support dashboard; and
8. measured public and productive outcomes.

The architecture is deliberately independent of any single software platform. Energy Access Explorer, energyRt and Pyomo are instruments inside AED; none controls the project's ontology, evidence rules or scientific identity.

## 2. Foundational doctrine

### 2.1 Africa as the primary system boundary

AED begins from African realities rather than adapting an external model after implementation. Its variables, data requirements, scenarios and validation rules must represent, where relevant:

- suppressed and unmet demand;
- weak-grid and off-grid conditions;
- critical public-service continuity;
- informal and small-enterprise productive activity;
- agriculture, irrigation, processing and cold chains;
- rapid urbanization and dispersed rural settlement;
- climate, heat, dust, flood and drought exposure;
- imported-fuel, currency, equipment and spare-part dependence;
- local engineering, operations and maintenance capability;
- regional power-pool and cross-border infrastructure conditions; and
- unequal access between central and peripheral territories.

### 2.2 Dignity as the objective

A connection is not equivalent to an adequate energy service. AED treats energy dignity as a multidimensional condition involving:

- access;
- reliability and continuity;
- affordability;
- quality and adequacy;
- productive-use capability;
- equity and inclusion;
- local capability and maintainability;
- resilience; and
- energy sovereignty.

No composite Energy Dignity Index is authorized by this architecture. Each dimension must first receive an operational definition, evidence source, unit or scale, uncertainty treatment and validation method.

### 2.3 Urgency as a design constraint

AED seeks to reduce the total time from verified need to productive service:

`Evidence → Decision → Engineering → Finance → Procurement → Construction → Commissioning → Productive Impact`

The rapidity objective is not permission to bypass safety, reliability, environmental protection, technical review or community safeguards. The preferred pathway is the fastest technically valid pathway satisfying approved constraints.

### 2.4 Leadership doctrine

AED adopts **Captain Ibrahim Traoré as its Africa Dignity Democracy leadership model**, centered on sovereignty, courage, national purpose, direct accountability, local mobilization and rapid execution.

Within AED, leadership is translated into measurable engineering and governance variables rather than an undefined symbolic score. These variables may include:

- decision lead time;
- approval lead time;
- accountable ownership of deliverables;
- procurement readiness;
- workforce mobilization time;
- corrective-action closure time;
- milestone reliability;
- local-capability transfer; and
- verified public-service outcomes.

The architecture remains institution-centered so that validated methods and capabilities survive changes in individual officeholders and administrations.

## 3. Intellectual lenses

Every approved AED module must pass seven questions.

| Lens | Architectural question |
|---|---|
| Engineering | Is the system buildable, safe, reliable, maintainable and deployable? |
| Mathematics | Are variables, equations, constraints, objectives and uncertainty explicit and testable? |
| Physics | Are energy, power, material, network, storage and environmental limits respected? |
| Public health | Does the system preserve life-critical services and reduce avoidable health exposure? |
| Philosophy | Does the decision increase African dignity, freedom, responsibility and intergenerational justice? |
| Leadership | Can the decision be executed rapidly, accountably and with visible public purpose? |
| Sovereignty | Does the system increase African control over energy, technology, data and productive capability? |

## 4. System-of-systems boundary

AED treats energy as an enabling infrastructure connected to:

- households and settlements;
- schools and digital learning;
- health facilities and medical cold chains;
- water pumping, treatment and sanitation;
- agriculture, irrigation, processing and refrigeration;
- enterprises, industry and mining;
- transport and mobility;
- telecommunications and digital systems;
- public administration and emergency services;
- regional electricity exchange; and
- climate adaptation and disaster response.

The architecture includes physical assets, institutions, users, markets, supply chains, workforce, data, software and governance interfaces.

It does not authorize real-time control of operating national power systems, statutory engineering approval, investment guarantees or country recommendations without country-specific validation.

## 5. Geographic architecture

AED uses a linked geographic hierarchy:

| Level | Purpose |
|---|---|
| Continental | African resource complementarity, strategic autonomy and scaling logic |
| Regional | Power pools, trade corridors, shared infrastructure and resilience |
| National | Sovereign planning, policy constraints and investment pathways |
| Subnational | Regions, provinces, communes, cities and productive zones |
| Local | Settlements, facilities, farms, enterprises and infrastructure sites |

### 5.1 Burkina Faso demonstration boundary

Burkina Faso is the first demonstration country. Architecture version `0.1` covers:

- one national energy-system layer;
- subnational geographic zones;
- households;
- critical health, education and water services;
- agriculture and productive uses;
- existing and candidate generation;
- storage;
- electricity imports and regional interconnection;
- reliability and resilience requirements;
- deployment constraints;
- local-capability indicators; and
- sovereignty indicators.

The Burkina Faso implementation must not be copied to another country without renewed data validation, institutional review and parameter calibration.

## 6. Logical architecture

```text
African realities, dignity and public purpose
                    ↓
Geospatial evidence and geographic prioritization
                    ↓
AED canonical data system
           ↙                     ↘
energyRt conventional       Native Pyomo AED
reference model             research model
           ↘                     ↙
          Cross-model verification
                    ↓
          Deployment engineering
                    ↓
          AED decision dashboard
                    ↓
Verified service, productive and sovereign outcomes
                    ↓
        Monitoring, learning and correction
```

## 7. Architectural layers

### Layer A — Evidence acquisition and geospatial diagnosis

**Purpose:** identify where energy deprivation, critical-service need, infrastructure opportunity, productive potential and hazard exposure occur.

**Primary inputs:** African official statistics, utilities, regulators, power pools, national geospatial agencies, research institutions, remote sensing and approved external platforms.

**Energy Access Explorer role:** upstream layer discovery, spatial analysis and geographic prioritization. It does not provide automatically approved optimization inputs.

**Required output:** traceable source records and candidate geospatial layers with publisher, date, resolution, unit, licence, access date, processing history, uncertainty and limitation.

### Layer B — AED canonical data system

**Purpose:** establish one platform-independent contract for evidence, geography, time, units, scenarios, uncertainty and validation.

The canonical layer is authoritative for all downstream modeling. Platform-specific source formats must be transformed through documented adapters.

**Required capabilities:**

- stable identifiers;
- explicit units;
- geographic hierarchy;
- temporal coverage and resolution;
- evidence classification;
- provenance and licensing;
- uncertainty representation;
- missing-data status;
- scenario and version control;
- validation status; and
- reproducible transformation history.

### Layer C — Conventional reference energy-system model

**Purpose:** represent standard capacity expansion, dispatch, commodities, technologies, resources, storage, demand, regions, time slices and trade.

**Reference implementation:** energyRt in a separate reproducible R environment, with an exact version pinned for each study.

This layer provides a conventional benchmark. It does not define AED-specific dignity, sovereignty, leadership or deployment mathematics unless those additions are separately specified and validated.

### Layer D — Native AED mathematical research model

**Purpose:** implement the equivalent conventional benchmark in Pyomo and then extend it with approved AED-specific formulations.

Potential approved extensions include:

- minimum critical-service constraints;
- affordability and energy-burden limits;
- productive-use capability;
- resilience and recovery requirements;
- strategic-dependency and sovereignty limits;
- local-capability and maintainability requirements;
- rapid-deployment variables and constraints; and
- uncertainty-aware scenarios.

No unapproved weighted composite score may be implemented.

### Layer E — Cross-model verification

**Purpose:** detect formulation, data, unit, indexing, temporal-aggregation and solver inconsistencies before AED-specific extensions are trusted.

The energyRt and Pyomo conventional benchmark models must consume equivalent canonical inputs and compare objective values, capacities, generation, trade, storage, unserved energy, balances, residuals and solver status.

### Layer F — Deployment engineering

**Purpose:** convert a technically preferred scenario into an executable program.

This layer represents:

- approvals;
- finance readiness;
- procurement;
- equipment lead times;
- supply-chain constraints;
- construction packages;
- workforce availability;
- commissioning;
- maintenance readiness;
- corrective action; and
- time to productive impact.

A model result is not a deployment plan until these constraints and responsibilities are explicit.

### Layer G — AED decision dashboard

**Purpose:** present verified evidence, model assumptions, scenarios, trade-offs, priorities, risks and outcomes.

The dashboard is a presentation and decision layer, not a source of scientific truth. It must not calculate undocumented indicators or display model outputs without run identifiers, source versions, units, scenario labels and validation status.

### Layer H — Monitoring, verification and learning

**Purpose:** compare planned and observed performance, detect failure and update data, models and deployment practice.

Observed operational outcomes must remain distinct from forecasts and scenarios. Corrections must be traceable to updated evidence or approved model changes.

## 8. Interface contracts

| Interface | Required transfer | Prohibited transfer |
|---|---|---|
| Evidence → canonical data | Source metadata, units, geography, time, licence, uncertainty and processing | Unattributed values or screenshots treated as data |
| EAE → canonical data | Individually registered and validated layers | Direct unverified transfer from visualization to model |
| Canonical data → energyRt | Approved conventional benchmark inputs | AED-specific assumptions hidden inside adapters |
| Canonical data → Pyomo | Equivalent conventional inputs plus separately approved AED extensions | Platform-specific undocumented defaults |
| energyRt ↔ Pyomo verification | Harmonized outputs and diagnostic metadata | Comparison without unit and time harmonization |
| Models → deployment | Technically feasible alternatives, constraints and uncertainties | Solver optimum presented as an executable project by itself |
| Models → dashboard | Validated run outputs and provenance | Unsourced or manually edited results |
| Operations → evidence | Observed performance and verified field records | Scenario values relabeled as observations |

## 9. Non-functional requirements

### 9.1 Reproducibility

Every model run must record code version, canonical-data version, scenario identifier, solver, solver version, options, runtime environment, timestamp and termination condition.

### 9.2 Traceability

Every decision-relevant value must be traceable to an observed source, published source, derived calculation, assumption, expert judgment or scenario choice.

### 9.3 Modularity

Geospatial, canonical-data, model, deployment and dashboard layers must be replaceable without rewriting the entire system.

### 9.4 Interoperability

Canonical data must remain independent of Energy Access Explorer, energyRt, Pyomo, a specific solver or a dashboard framework.

### 9.5 Verification before interpretation

Model feasibility, balances, constraints, termination condition and numerical residuals must be checked before policy or deployment interpretation.

### 9.6 African data and capability sovereignty

AED must preserve African institutional control over decision logic, model documentation, locally generated evidence and capacity to reproduce results.

### 9.7 Security and ethics

Restricted infrastructure, personal, facility-security or community data must not be published without authorization. Geographic precision must be reduced when disclosure creates material risk.

## 10. Decision and evidence states

### Evidence classes

- `observed`
- `published`
- `derived`
- `assumed`
- `scenario`
- `expert_judgment`
- `unverified`

### Validation states

- `proposed`
- `schema_valid`
- `source_verified`
- `cross_checked`
- `model_ready`
- `validated`
- `rejected`
- `deprecated`

No evidence class or validation state may be silently upgraded.

## 11. Scenario and model-run identity

Every scenario must have a stable identifier, human-readable name, version, geographic scope, planning horizon, policy assumptions, data version and status.

Every model run must have a unique run identifier linking:

- scenario;
- model implementation;
- code commit;
- data release;
- solver and options;
- execution timestamp;
- result files; and
- verification report.

## 12. Scaling pathway

### Stage 1 — Burkina Faso

Validate the architecture, data contract, conventional benchmark, AED extensions and deployment logic in one country.

### Stage 2 — Sahel comparison

Add selected Sahel countries through country-specific adapters and validation. Compare shared constraints without assuming parameter equivalence.

### Stage 3 — Regional power-system integration

Represent power-pool trade, corridors, complementarity, shared reserves and regional resilience.

### Stage 4 — Wider African scaling

Expand to additional African regions while preserving country ownership, contextual validation and interoperable continental indicators.

## 13. Explicit exclusions for ARCH-001

This architecture branch does not authorize:

- production dashboard code;
- full Burkina Faso data ingestion;
- complete energyRt or Pyomo implementation;
- new software dependencies;
- automated Energy Access Explorer scraping;
- unsupported numerical parameters;
- country-level recommendations;
- an aggregate Energy Dignity Index; or
- physical deployment claims.

## 14. Architectural decisions frozen in version 0.1

1. Burkina Faso is the first demonstration country.
2. The canonical data system is platform-independent and authoritative downstream.
3. Energy Access Explorer is an upstream geospatial benchmark and source-discovery instrument.
4. energyRt is an optional conventional reference model maintained in a separate R environment.
5. Native Pyomo is the AED-specific research model and must first reproduce the conventional benchmark.
6. Equivalent models must pass cross-model verification before AED-specific interpretations are accepted.
7. Deployment engineering is separate from mathematical optimization but consumes verified model outputs.
8. The dashboard displays verified results; it does not define scientific truth.
9. Leadership enters through measurable execution variables and public outcomes.
10. No country conclusion is valid without country-specific evidence and validation.

## 15. Unresolved decisions

The following remain for follow-on issues:

- exact Burkina Faso subnational zoning system;
- approved temporal resolution and representative time-slice design;
- exact solver set for benchmark verification;
- dataset-specific licensing decisions;
- per-variable numerical comparison tolerances;
- formal definitions of local capability and sovereignty parameters;
- security classification for sensitive infrastructure data; and
- institutional owners for each Burkina Faso canonical dataset.

## 16. Approval conditions

Architecture version `0.1` is approved when:

- all six ARCH-001 documents are reviewed together;
- tool responsibilities and prohibitions are consistent;
- the canonical data contract supports all approved layers;
- cross-model verification rules are operationally specified;
- unresolved decisions are explicitly assigned to follow-on issues; and
- no implementation work has been introduced prematurely.

## References

- Africa Energy Dignity, `README.md`, project charter and scientific foundation.
- World Resources Institute, Energy Access Explorer methodology and attribution requirements: https://training.energyaccessexplorer.org/about/ and https://www.energyaccessexplorer.org/attribution/
- energyRt official documentation: https://energyrt.org/
- Pyomo official documentation: https://pyomo.readthedocs.io/
