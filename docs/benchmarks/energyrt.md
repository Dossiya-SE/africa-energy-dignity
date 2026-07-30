# energyRt Benchmark for Africa Energy Dignity

**Document ID:** `AED-BENCH-ERT-001`  
**Version:** `0.1`
**Status:** Approved architecture baseline
**Issue:** `ARCH-001` / Issue #3  
**Initial application:** Burkina Faso

## 1. Purpose

This document defines the approved role of energyRt inside Africa Energy Dignity (AED), the conditions under which it may be used, and the benchmark required before it informs the AED optimization architecture.

energyRt is treated as an optional conventional reference energy-system model. It is not the intellectual center of AED and does not replace native Pyomo, the canonical data system, deployment engineering or the AED dashboard.

## 2. Approved role

energyRt may be used to:

- represent conventional energy commodities, technologies, resources, demand, storage, trade, regions, years and time slices;
- construct a small Burkina Faso capacity-expansion and dispatch reference system;
- accelerate prototyping of standard energy-system equations;
- generate benchmark outputs for comparison with a native Pyomo implementation;
- test the adequacy of AED canonical input structures for conventional modeling; and
- provide an independent implementation path for verification.

## 3. Architectural position

```text
AED canonical conventional inputs
              ↓
       energyRt adapter
              ↓
energyRt reference formulation
              ↓
Approved solver/backend
              ↓
Common AED result contract
              ↓
Cross-model verification against native Pyomo
```

energyRt object structures must not become the canonical AED data model. The adapter is responsible for mapping approved AED identifiers, units, time slices and scenario values into the energyRt runtime.

## 4. Required technical assessment

Before implementation, the benchmark must document:

- exact energyRt release or commit;
- R version;
- installation method;
- dependency lock mechanism;
- supported operating systems;
- selected mathematical-programming backend;
- selected solver;
- solver version and licence;
- supported commodities and technology structures;
- storage representation;
- trade representation;
- regional representation;
- time-slice representation;
- scenario-management behavior;
- result extraction and reporting;
- custom-constraint mechanism;
- numerical tolerances; and
- known limitations.

## 5. Reproducibility requirements

Every energyRt benchmark must include:

- a pinned energyRt version or commit;
- a reproducible R environment, preferably with a lock file;
- explicit solver installation instructions;
- complete input-to-object mapping;
- scenario identifier;
- canonical data release identifier;
- execution script;
- result export script;
- runtime metadata;
- solver termination information; and
- a generated comparison package.

Unpinned installation from a moving development branch is prohibited for an approved benchmark.

## 6. Licensing boundary

The official energyRt project is distributed under the GNU Affero General Public License version 3 or later. AED currently uses the Apache License 2.0 for its own software.

Therefore:

- energyRt source code must not be copied into AED without a documented licence review;
- energyRt should initially remain a separately installed dependency and runtime;
- derivative-work implications must be reviewed before tight integration or redistribution;
- the exact energyRt version and licence notice must be recorded;
- model inputs and AED-authored adapter code must have clearly documented licensing; and
- no architecture statement should imply that energyRt itself is relicensed under Apache 2.0.

This document records an engineering boundary, not legal advice. A formal licensing review is required before distribution decisions.

## 7. Minimum Burkina Faso reference system

The first benchmark must remain deliberately small and transparent.

### 7.1 Geography

- one national region initially;
- optional second zone only if necessary to test trade or transfer;
- no unsupported subnational detail.

### 7.2 Commodities

- electricity;
- one imported fuel commodity where required;
- optional unserved-energy or slack representation documented explicitly.

### 7.3 Technologies

At minimum:

- solar photovoltaic;
- one dispatchable thermal technology;
- electricity import technology or trade link;
- optional storage after the base case is verified.

Hydropower, wind and additional technologies may be added only with approved canonical inputs.

### 7.4 Demand

- one annual or time-sliced electricity demand series;
- explicit unit;
- documented source or synthetic benchmark status;
- served and unserved demand accounting.

### 7.5 Planning horizon

- one base period and one planning period, or the minimum structure supported by the approved benchmark;
- explicit discounting and annualization assumptions.

## 8. Required conventional equations

The benchmark must document how energyRt represents:

- commodity balance;
- technology activity;
- capacity and availability;
- new investment;
- existing capacity;
- operating cost;
- investment cost;
- import or trade cost;
- demand satisfaction;
- unserved-energy penalty;
- storage balance when enabled;
- capacity or resource potential; and
- objective function.

The documentation must identify any defaults automatically introduced by energyRt.

## 9. Canonical input mapping

At minimum, the adapter must map:

| AED canonical family | energyRt target concept |
|---|---|
| Geography | Region |
| Commodity | Commodity |
| Technology | Technology |
| Resource or fuel | Supply or commodity input |
| Demand | Demand object or equivalent |
| Storage technology | Storage object |
| Trade link | Trade object |
| Time structure | Year and time-slice sets |
| Existing capacity | Capacity parameter |
| Candidate capacity | Investment decision and limits |
| Cost | Investment, fixed, variable, fuel or trade cost |
| Availability profile | Activity or capacity-factor parameter |
| Policy constraint | Approved standard or custom constraint |

Every mapping must preserve AED identifiers in a crosswalk table.

## 10. Required result export

energyRt results must be exported into a common AED comparison structure containing, where applicable:

- scenario identifier;
- run identifier;
- region;
- period and time slice;
- commodity;
- technology;
- existing capacity;
- new capacity;
- total capacity;
- activity or generation;
- imports and exports;
- storage charge;
- storage discharge;
- state of charge;
- served demand;
- unserved energy;
- cost component;
- total objective value;
- constraint or balance residual;
- solver status; and
- runtime.

## 11. Verification role

energyRt is valuable to AED only if it strengthens verification.

The reference model must be mathematically matched by a native Pyomo model using equivalent canonical inputs. Comparison must not begin until:

- units are harmonized;
- time-slice weights are aligned;
- cost annualization is aligned;
- discounting is aligned;
- capacity conventions are aligned;
- storage boundary conditions are aligned;
- solver tolerances are recorded; and
- slack and unserved-energy treatment are equivalent.

## 12. AED-specific extensions

The following are not part of the initial energyRt benchmark unless separately approved:

- energy-dignity minimum-service rules;
- affordability or energy-burden limits;
- sovereignty constraints;
- African engineering and local-capability constraints;
- rapid-deployment sequencing;
- public-health continuity constraints;
- composite leadership metrics;
- procurement and workforce scheduling.

Some extensions may eventually be represented through custom constraints, but native Pyomo remains the primary AED research implementation until equivalence and extensibility are demonstrated.

## 13. Risks

| Risk | Control |
|---|---|
| Moving development version | Pin exact release or commit |
| R and Python environment complexity | Maintain separate reproducible environments |
| Licence incompatibility or ambiguity | Keep energyRt separate and conduct review |
| Hidden defaults | Document generated formulation and parameter defaults |
| Unit or time mismatch | Use canonical adapters and comparison checks |
| False confidence from software agreement | Preserve empirical validation as a separate requirement |
| Tight coupling | Keep the core AED Python package independent |
| Duplicate model maintenance | Restrict energyRt to the approved reference benchmark role |

## 14. Decision criteria

After the benchmark, AED must decide whether energyRt should be:

- retained as a permanent reference model;
- retained only for selected benchmark cases;
- used as a rapid scenario prototyping tool;
- used through its Pyomo backend where technically justified; or
- excluded from production workflows while preserving the benchmark documentation.

The decision must consider:

- mathematical coverage;
- reproducibility;
- transparency;
- extensibility;
- performance;
- maintenance burden;
- licensing;
- African institutional usability; and
- cross-model verification value.

## 15. Required outputs for `MODEL-002`

- pinned energyRt environment;
- minimum Burkina Faso reference model;
- complete equation and default mapping;
- canonical input adapter specification;
- common result export;
- solver and runtime report;
- licence assessment record;
- limitations register; and
- recommendation for the continuing role of energyRt.

## 16. Acceptance criteria

The benchmark is approved when:

- the exact energyRt version is pinned;
- R and solver environments are reproducible;
- the minimum model is fully documented;
- canonical data remain authoritative;
- outputs follow the common comparison contract;
- licensing implications are documented;
- no AED-specific claim is made before cross-model verification;
- no energyRt source is copied into AED without review.

## 17. References

- energyRt official site and documentation: https://energyrt.org/
- energyRt model documentation: https://energyrt.org/articles/model.html
- energyRt use with R documentation: https://energyrt.org/articles/use-R-2026.html
