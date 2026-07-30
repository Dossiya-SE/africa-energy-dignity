# AED Cross-Model Verification Protocol

**Document ID:** `AED-VANDV-001`  
**Version:** `0.1`
**Status:** Approved architecture baseline
**Issue:** `ARCH-001` / Issue #3  
**Initial application:** Burkina Faso conventional benchmark

## 1. Purpose

This document defines how Africa Energy Dignity (AED) will verify mathematical equivalence between the conventional energy-system formulation implemented in energyRt and the equivalent formulation implemented natively in Pyomo.

Cross-model verification is intended to detect formulation, indexing, unit, data-mapping, temporal-aggregation, solver and implementation errors before AED-specific dignity, sovereignty, resilience, local-capability or rapid-deployment mathematics are accepted.

Agreement between two models does not by itself establish empirical validity. Cross-model verification is one layer within the wider AED verification and validation system.

## 2. Scope

The initial comparison covers the minimum approved Burkina Faso conventional benchmark:

- one national region;
- electricity demand;
- solar photovoltaic generation;
- one dispatchable thermal technology;
- electricity imports or an equivalent trade representation;
- investment and operating costs;
- capacity and activity limits;
- served and unserved demand;
- one planning period;
- optional storage only after the non-storage benchmark passes.

AED-specific research constraints are excluded from the first equivalence test.

## 3. Verification principles

1. Both models consume the same approved canonical inputs.
2. All units and time weights are harmonized before comparison.
3. Mathematical formulations are compared before numerical results.
4. Solver status is checked before output comparison.
5. Infeasibility is reported, not hidden through uncontrolled slack.
6. Absolute and relative tolerances are both used.
7. Multiple optimal solutions are treated explicitly.
8. Disagreement triggers diagnosis, not averaging.
9. Verification evidence is versioned and reproducible.
10. A passing comparison is required before AED-specific interpretation.

## 4. Comparison architecture

```text
Approved canonical benchmark dataset
             ↙                 ↘
   energyRt adapter       Pyomo adapter
             ↓                 ↓
 energyRt formulation     Pyomo formulation
             ↓                 ↓
  solver execution         solver execution
             ↘                 ↙
       common result contract
                  ↓
      normalization and checks
                  ↓
       equivalence assessment
                  ↓
 diagnostic report and approval status
```

## 5. Pre-solve equivalence review

Before executing either model, reviewers must confirm equivalence of:

- sets and indices;
- geography;
- planning periods;
- time slices and weights;
- commodities;
- technologies;
- existing capacities;
- candidate capacity bounds;
- demand values;
- availability or capacity factors;
- efficiency conventions;
- cost definitions;
- annualization and discounting;
- import representation;
- unserved-energy representation;
- storage equations and boundary conditions when applicable;
- objective sense and components;
- constraint directions; and
- variable domains.

The pre-solve review must produce a signed or approved formulation crosswalk.

## 6. Canonical input identity

Every comparison run must reference one immutable canonical benchmark release containing:

- dataset release identifier;
- scenario identifier;
- geographic identifier;
- variable definitions;
- units;
- time structure;
- source or assumption status;
- version;
- checksum or equivalent integrity record.

Model-specific input files must be generated from that release through documented adapters. Manual duplication of values is not an approved workflow.

## 7. Solver controls

The comparison must record:

- solver name;
- solver version;
- interface or backend;
- feasibility tolerance;
- optimality tolerance;
- integer tolerance when applicable;
- time limit;
- relative and absolute optimality gap;
- scaling options;
- presolve settings where relevant;
- random seed where relevant;
- termination condition; and
- solver message.

Where possible, both implementations should first use the same solver. A second-solver comparison may follow to distinguish formulation disagreement from solver-specific behavior.

## 8. Required comparison variables

At minimum, compare:

### 8.1 System-level outputs

- total objective value;
- total discounted or annualized cost;
- total served demand;
- total unserved energy;
- total imports;
- renewable share;
- solver termination condition;
- feasibility status;
- runtime.

### 8.2 Technology-level outputs

- existing installed capacity;
- new capacity;
- total capacity;
- generation or activity;
- fuel or commodity input;
- fixed cost;
- variable cost;
- investment cost.

### 8.3 Time- and region-level outputs

- demand;
- generation;
- imports and exports;
- curtailment if represented;
- unserved energy;
- energy-balance residual.

### 8.4 Storage outputs when enabled

- storage power capacity;
- storage energy capacity;
- charge;
- discharge;
- state of charge;
- losses;
- initial and terminal state conditions.

### 8.5 Constraint diagnostics

- lower and upper bounds;
- constraint activity;
- residual or slack;
- binding status;
- dual or marginal value where both implementations and solvers support comparable values.

## 9. Common result contract

Each result record must contain:

- `comparison_id`;
- `run_id`;
- `model_implementation`;
- `scenario_id`;
- `geography_id`;
- `period`;
- `time_slice`;
- `entity_type`;
- `entity_id`;
- `metric`;
- `value`;
- `unit`;
- `solver_status`;
- `validation_status`;
- `source_commit`;
- `data_release`;
- `created_at`.

Both adapters must export to this structure before comparison.

## 10. Numerical comparison rules

For values `a` and `b`, calculate:

- absolute deviation: `abs(a - b)`;
- relative deviation: `abs(a - b) / max(abs(a), abs(b), scale_floor)`.

A value passes when either the absolute deviation is below the approved absolute tolerance or the relative deviation is below the approved relative tolerance, unless the metric has a stricter domain-specific rule.

### 10.1 Provisional default tolerances

The following are architecture defaults for the first continuous linear benchmark and must be reviewed in `VANDV-002`:

| Metric | Absolute tolerance | Relative tolerance |
|---|---:|---:|
| Objective value | `1e-6` in normalized comparison units | `1e-6` |
| Capacity | `1e-6 MW` | `1e-6` |
| Energy or generation | `1e-6 MWh` | `1e-6` |
| Cost component | `1e-6` in normalized currency units | `1e-6` |
| Balance residual | `1e-7 MWh` | Not applicable |
| Storage state | `1e-6 MWh` | `1e-6` |

These values are provisional. They must be adjusted when model scaling, solver precision or integer variables justify a different threshold. Any change must be documented before the comparison is run.

## 11. Multiple optimal solutions

Two models may produce different technology-level solutions with the same objective value when the mathematical problem has alternative optima.

When this occurs:

1. confirm both solutions satisfy all constraints;
2. confirm objective values agree within tolerance;
3. identify degenerate or substitutable variables;
4. compare aggregate quantities;
5. optionally introduce a documented secondary objective or lexicographic rule for diagnostic purposes;
6. do not classify the difference as implementation failure solely because variable values differ.

Secondary objectives used for diagnosis must not become policy preferences without approval.

## 12. Infeasibility protocol

If one or both models are infeasible:

- preserve the original solver status;
- do not silently add or enlarge slack variables;
- check demand, capacity, resource and policy bounds;
- compare all canonical inputs;
- use solver infeasibility diagnostics where available;
- identify the smallest conflicting constraint set where possible;
- document whether infeasibility is physical, policy-induced, data-induced or implementation-induced.

A model is not verified when one implementation is feasible and the other is infeasible under equivalent inputs.

## 13. Diagnostic sequence for failed equivalence

Investigate in this order:

1. Identifier and data-release mismatch
2. Unit conversion
3. Time-slice weights and annualization
4. Demand sign and balance convention
5. Capacity versus activity units
6. Efficiency convention
7. Existing-capacity and investment treatment
8. Cost discounting and price-year treatment
9. Import and export direction
10. Unserved-energy or slack formulation
11. Storage initial and terminal conditions
12. Variable domains and bounds
13. Constraint direction and indexing
14. Solver tolerance and scaling
15. Alternative optima
16. Software defect

Every diagnosed discrepancy must receive a disposition: corrected, accepted with rationale, deferred or blocking.

## 14. Verification levels

| Level | Requirement |
|---|---|
| `V0 — Structural` | Sets, variables, parameters, objectives and constraints mapped |
| `V1 — Input` | Canonical inputs and units identical after adapter transformation |
| `V2 — Feasibility` | Both models reach compatible feasible status |
| `V3 — Objective` | Objective values agree within tolerance |
| `V4 — Aggregate outputs` | Capacity, generation, imports and unserved energy agree |
| `V5 — Detailed outputs` | Technology, region and time-slice results agree or alternative optima are explained |
| `V6 — Residuals` | Balances and binding constraints pass numerical checks |
| `V7 — Reproduction` | Independent clean-environment rerun reproduces the result |

The conventional benchmark is approved only after `V7`.

## 15. Verification tests

Required automated checks include:

- canonical input checksums match;
- expected sets and dimensions match;
- unit conversions are reversible;
- demand totals match;
- time-slice weights reconstruct the modeled period;
- objective components sum to the reported objective;
- energy balances close;
- capacity and resource constraints are respected;
- non-negativity and domains are respected;
- result records use known canonical identifiers;
- solver termination is approved;
- tolerances are applied consistently.

## 16. Empirical validation boundary

Cross-model agreement does not prove that:

- demand forecasts are correct;
- technology costs are current;
- infrastructure data are complete;
- deployment is feasible;
- political or institutional assumptions are realistic;
- public outcomes will occur.

Empirical validation requires observed Burkina Faso evidence, operator review, field measurements, historical comparison and stakeholder assessment under separate issues.

## 17. Approval rule for AED-specific extensions

Native Pyomo may proceed to AED-specific dignity, sovereignty, resilience, productive-use, local-capability and rapidity extensions only when:

- the conventional benchmark reaches `V7`;
- unresolved deviations are non-blocking and documented;
- the approved canonical data contract is in use;
- the mathematical specification for each extension is reviewed;
- tests are defined before interpretation.

energyRt is not required to reproduce every AED-specific extension unless a separate verification plan approves that use.

## 18. Required verification report

The report must contain:

- objective and scope;
- model and data versions;
- formulation crosswalk;
- solver settings;
- tolerance table;
- input identity checks;
- result comparison tables;
- residual analysis;
- alternative-optimum analysis;
- discrepancies and diagnoses;
- verification level achieved;
- limitations;
- approval status;
- reviewer names and date.

## 19. Acceptance criteria

The protocol is approved when:

- equivalent inputs are guaranteed by canonical adapters;
- all required metrics are defined;
- tolerance logic is explicit;
- multiple optimal solutions are handled correctly;
- infeasibility is not hidden;
- residual and solver-status checks are mandatory;
- empirical validation remains a distinct requirement;
- progression to AED-specific mathematics is gated by successful verification.

## 20. Follow-on work

`VANDV-002` will implement this protocol, approve metric-specific tolerances, generate the common comparison schema and produce the first Burkina Faso equivalence report.
