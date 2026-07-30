# AED Tool Responsibility Matrix

**Document ID:** `AED-ARCH-002`  
**Version:** `0.1`
**Status:** Approved architecture baseline
**Issue:** `ARCH-001` / Issue #3

## 1. Purpose

This document freezes the responsibilities, interfaces and exclusions of the principal tools and layers used by Africa Energy Dignity (AED).

The central rule is:

> No tool may silently expand beyond its approved responsibility boundary.

Energy Access Explorer, energyRt, native Pyomo, deployment engineering and the AED dashboard are coordinated components inside AED. The AED canonical data system remains the platform-independent authority connecting them.

## 2. Responsibility matrix

| Component | Authoritative responsibility | Required inputs | Required outputs | Explicit exclusions |
|---|---|---|---|---|
| African official and scientific sources | Primary evidence about population, facilities, infrastructure, demand, resources, costs, hazards and institutions | Original measurements, administrative records, surveys, technical reports and approved remote-sensing products | Traceable source records and datasets | No automatic acceptance without provenance and quality assessment |
| Energy Access Explorer | Upstream geospatial diagnosis, layer discovery, spatial filtering and geographic prioritization | Registered geospatial layers and user-defined criteria | Candidate priority areas, layer metadata and reproducible spatial-analysis notes | Not the AED database, optimization engine, deployment scheduler or final authority for country recommendations |
| AED canonical data system | Platform-independent definitions, identifiers, units, geography, time, evidence class, provenance, licensing, uncertainty, scenarios and validation state | Approved source records and documented transformations | Validated canonical records consumed by all downstream components | Must not depend on EAE, energyRt, Pyomo, one solver or one dashboard framework |
| energyRt | Optional conventional reference model for capacity expansion, dispatch, commodities, technologies, resources, storage, demand, regions, time slices and trade | Canonical conventional energy-system inputs | Conventional benchmark results and model diagnostics | Does not define AED-specific dignity, sovereignty, leadership or deployment mathematics by default |
| Native Pyomo | AED-specific mathematical research implementation and independent reproduction of the conventional benchmark | Equivalent canonical benchmark inputs plus separately approved AED extensions | Verified conventional results, AED-specific scenarios, residuals and solver diagnostics | Must not bypass cross-model verification or implement unapproved composite scores |
| Cross-model verification | Detect inconsistencies between equivalent conventional formulations | Harmonized canonical inputs and model outputs | Equivalence report, deviations, residuals and diagnostic explanation | Not a third optimization model and not a substitute for empirical validation |
| Deployment engineering | Convert verified scenarios into executable delivery plans | Verified model alternatives, institutional constraints, workforce, procurement, finance and construction information | Sequenced packages, schedules, readiness states, responsibilities, risks and commissioning requirements | Cannot declare implementation readiness from optimization results alone |
| AED dashboard | Present verified evidence, scenarios, trade-offs, risks, priorities and outcomes | Validated canonical data, verified model runs and approved deployment outputs | Maps, charts, reports and traceable decision views | Must not create undocumented metrics, overwrite source data or display unverified results as facts |
| Monitoring and learning | Compare planned and observed performance and trigger correction | Operational records, service measurements, maintenance events and verified field evidence | Updated evidence, performance reports, corrective-action records and recalibration inputs | Must not relabel forecasts or assumptions as observed evidence |

## 3. Authority hierarchy

When components disagree, the following authority order applies:

1. Verified physical and operational evidence
2. Approved canonical definitions and units
3. Reproducible transformation logic
4. Verified mathematical formulation
5. Solver output with valid termination status
6. Deployment interpretation
7. Dashboard presentation

A dashboard display never overrides a canonical definition. A solver optimum never overrides a physical constraint. A platform-specific default never overrides an approved AED requirement.

## 4. Energy Access Explorer boundary

### Approved uses

- Discover potentially relevant geospatial layers.
- Inspect geographic coverage and resolution.
- Conduct transparent overlays, filters, buffers and multi-criteria prioritization.
- Identify candidate areas for deeper Burkina Faso analysis.
- Record original publishers and datasets for the AED source register.
- Benchmark AED map organization and spatial decision workflows.

### Required controls

Every adopted layer must record:

- original publisher;
- original dataset name;
- source URL or persistent identifier;
- access date;
- spatial resolution;
- temporal coverage;
- unit;
- licence and attribution requirement;
- processing history;
- uncertainty or known limitation; and
- AED validation status.

### Prohibited uses

- Unauthorized scraping.
- Treating a visualization as a canonical dataset.
- Copying values without original-source provenance.
- Feeding unverified displayed values directly into optimization.
- Reproducing the full platform as AED's primary contribution.
- Presenting EAE-derived priorities as final investment decisions.

## 5. energyRt boundary

### Approved uses

- Rapid construction of a conventional reference energy system.
- Representation of commodities, technologies, resources, storage, trade, demand, regions, years and time slices.
- Scenario benchmarking.
- Generation of conventional capacity-expansion and dispatch results.
- Independent reference for the native Pyomo benchmark.

### Required controls

- Pin the exact version or commit.
- Maintain a separate reproducible R environment.
- Document all solver and backend choices.
- Record AGPL licensing implications before distribution or integration decisions.
- Use canonical inputs rather than manually duplicated model-specific values.
- Export results to the approved AED comparison schema.

### Prohibited uses

- Tight coupling to the core AED Python package.
- Allowing energyRt object names to define the canonical ontology.
- Copying source code into AED without licence review.
- Treating energyRt outputs as empirically validated outcomes.
- Adding AED-specific constructs without a separate mathematical specification.

## 6. Native Pyomo boundary

### Approved uses

- Reproduce the approved conventional reference model.
- Implement transparent AED-specific mathematical constraints.
- Support explicit experimentation with dignity, sovereignty, productive-use, resilience, local-capability and rapidity formulations.
- Expose variables, constraints, objectives, duals where supported and residuals for verification.

### Required controls

- Match canonical units and indexing.
- Check solver availability and termination condition.
- Report infeasibility explicitly.
- Test balances, bounds, domains and extreme cases.
- Separate input data from model code.
- Preserve run metadata and reproducibility.
- Pass conventional cross-model verification before AED-specific interpretation.

### Prohibited uses

- Hidden constants.
- Unsupported country data.
- Undocumented objective weights.
- Silent relaxation of critical constraints.
- Presenting infeasible or non-optimal results as valid plans.
- Implementing a composite Energy Dignity Index without approval.

## 7. Cross-model verification boundary

Cross-model verification compares equivalent conventional systems only.

It must compare, where applicable:

- objective value;
- installed and new capacity;
- generation;
- fuel or commodity flows;
- imports and exports;
- storage charge, discharge and state of charge;
- served and unserved demand;
- renewable share;
- energy balances;
- capacity constraints;
- residuals;
- solver status; and
- infeasibility diagnostics.

It must distinguish among:

- formulation differences;
- unit differences;
- time-aggregation differences;
- solver-tolerance differences;
- multiple optimal solutions;
- data-mapping errors; and
- implementation defects.

## 8. Deployment engineering boundary

Deployment engineering begins only after a technically valid scenario exists.

It must represent:

- decision and approval gates;
- financing readiness;
- procurement packages;
- supplier qualification;
- equipment lead times;
- logistics and access;
- workforce availability;
- construction sequence;
- commissioning;
- operations and maintenance readiness;
- spare parts;
- corrective actions; and
- accountable ownership.

Deployment engineering may reject or modify a model-preferred scenario when implementation constraints make it unsafe, unavailable or non-maintainable. Such changes must be documented and, where relevant, returned to the model as revised constraints.

## 9. Dashboard boundary

The dashboard may:

- display source-controlled maps;
- show data status and uncertainty;
- allow approved scenario selection;
- display verified model outputs;
- compare trade-offs;
- show deployment readiness and risks;
- export traceable reports.

The dashboard must always expose:

- data version;
- scenario identifier;
- model-run identifier;
- units;
- source or provenance link;
- validation status;
- uncertainty or limitation; and
- last update date.

It may not calculate hidden policy scores, silently interpolate missing data or allow users to alter canonical records without an approved data workflow.

## 10. Required interfaces

| Interface | Contract owner | Required artifact |
|---|---|---|
| Source to canonical data | Data governance | Source record and transformation record |
| EAE to canonical data | Geospatial workstream | Layer adoption record |
| Canonical data to energyRt | Modeling architecture | energyRt adapter specification |
| Canonical data to Pyomo | Modeling architecture | Pyomo adapter specification |
| energyRt to comparison layer | Verification workstream | Common result export |
| Pyomo to comparison layer | Verification workstream | Common result export |
| Models to deployment engineering | Deployment workstream | Verified scenario package |
| Models and deployment to dashboard | Dashboard workstream | Approved API or result contract |
| Operations to canonical evidence | Monitoring workstream | Field observation and update record |

## 11. Change-control rule

Any proposal that changes a component's responsibility must:

1. identify the affected interface;
2. state the scientific or engineering reason;
3. assess licensing and reproducibility impacts;
4. update the canonical data contract if necessary;
5. update verification requirements;
6. receive architecture review before implementation.

## 12. Frozen decisions

- Energy Access Explorer remains upstream and geospatial.
- The AED canonical data system remains platform-independent and authoritative.
- energyRt remains an optional conventional reference model.
- Native Pyomo remains the AED-specific research implementation.
- Cross-model verification is mandatory for equivalent conventional formulations.
- Deployment engineering is a separate executable-planning layer.
- The dashboard is a verified presentation layer, not the scientific authority.
