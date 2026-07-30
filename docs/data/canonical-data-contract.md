# AED Canonical Data Contract

**Document ID:** `AED-DATA-001`  
**Version:** `0.1-draft`  
**Status:** Architecture approval candidate  
**Issue:** `ARCH-001` / Issue #3  
**Initial geography:** Burkina Faso

## 1. Purpose

This document defines the platform-independent contract that all Africa Energy Dignity (AED) data must satisfy before use in geospatial analysis, energy-system modeling, deployment engineering or dashboard presentation.

The canonical data layer is the authoritative interface between source evidence and downstream tools. It must remain independent of Energy Access Explorer, energyRt, Pyomo, any solver and any dashboard framework.

## 2. Core principles

1. Every decision-relevant value has an explicit definition and unit.
2. Every observed or published value has traceable provenance.
3. Facts, derived values, assumptions, expert judgments and scenarios remain distinct.
4. Geographic and temporal resolution are explicit.
5. Missingness and uncertainty are represented, never hidden.
6. Raw evidence is never silently overwritten.
7. All transformations are reproducible.
8. Canonical identifiers are stable across tools.
9. Country-specific validation is mandatory before country conclusions.
10. Sensitive infrastructure and personal data receive appropriate protection.

## 3. Canonical record envelope

Every canonical record must contain the following fields where applicable.

| Field | Requirement | Description |
|---|---|---|
| `record_id` | Required | Stable globally unique AED record identifier |
| `entity_type` | Required | Record class such as geography, demand, technology, facility, resource or policy |
| `entity_id` | Required | Stable identifier for the represented entity |
| `name` | Required | Human-readable name |
| `variable` | Required | Machine-readable variable name |
| `definition` | Required | Unambiguous scientific or engineering definition |
| `value` | Conditional | Numeric, categorical, Boolean or structured value |
| `unit` | Conditional | Approved unit when the value is dimensional |
| `geography_id` | Conditional | Link to the canonical geographic hierarchy |
| `spatial_resolution` | Conditional | Point, raster resolution, administrative level or network element |
| `valid_from` | Conditional | Beginning of validity or observation period |
| `valid_to` | Conditional | End of validity or observation period |
| `temporal_resolution` | Conditional | Instantaneous, hourly, daily, monthly, annual or model time slice |
| `evidence_class` | Required | Observed, published, derived, assumed, scenario, expert judgment or unverified |
| `source_id` | Conditional | Link to the canonical source register |
| `processing_method` | Required for derived data | Reproducible transformation description or code reference |
| `uncertainty_type` | Conditional | Range, standard deviation, confidence interval, distribution or qualitative class |
| `uncertainty_value` | Conditional | Structured uncertainty value |
| `missing_status` | Required | Not missing, not collected, unavailable, suppressed, not applicable or imputed |
| `scenario_id` | Conditional | Link to a scenario when the record is scenario-dependent |
| `validation_status` | Required | Current validation state |
| `responsible_contributor` | Required | Accountable person or institution |
| `version` | Required | Record or dataset version |
| `created_at` | Required | Creation timestamp |
| `updated_at` | Required | Last update timestamp |

## 4. Evidence classification

Allowed evidence classes are:

| Class | Meaning |
|---|---|
| `observed` | Directly measured, administratively recorded or officially reported |
| `published` | Reported in a traceable external publication or dataset |
| `derived` | Calculated from documented inputs through a reproducible method |
| `assumed` | Introduced explicitly for model construction or testing |
| `scenario` | Selected to represent a possible future or policy condition |
| `expert_judgment` | Supplied by a qualified reviewer with identity and rationale recorded |
| `unverified` | Not yet acceptable for decision use |

A record must never change evidence class without a documented review event.

## 5. Validation states

Allowed validation states are:

- `proposed`
- `schema_valid`
- `source_verified`
- `cross_checked`
- `model_ready`
- `validated`
- `rejected`
- `deprecated`

### Minimum meaning

- `schema_valid` means the record satisfies the data structure and unit rules.
- `source_verified` means the source exists and supports the recorded value.
- `cross_checked` means the value has been compared with another credible source or internal consistency rule.
- `model_ready` means the value is approved for a defined model scope.
- `validated` means it has passed the complete approved process for its intended use.

## 6. Source register contract

Every source must have a stable `source_id` and include:

- title;
- original publisher;
- authors or institutional owner where available;
- source URL, DOI or persistent identifier;
- publication or release date;
- access date;
- geographic coverage;
- temporal coverage;
- original units and definitions;
- licence or terms of use;
- attribution requirements;
- data-access method;
- known limitations;
- archived copy or checksum where legally permitted;
- verification status; and
- responsible reviewer.

A platform displaying a dataset is not automatically the original source. The original publisher and original dataset must be recorded whenever discoverable.

## 7. Geography contract

### 7.1 Geographic hierarchy

The canonical hierarchy must support:

- continent;
- African region;
- regional power pool;
- country;
- first-order administrative area;
- lower administrative areas;
- settlement or cluster;
- facility or infrastructure site;
- network node or corridor; and
- raster or grid cell.

### 7.2 Required geographic fields

Each geographic entity must include:

- `geography_id`;
- `name`;
- `geography_type`;
- `parent_geography_id`;
- official code where available;
- geometry type;
- coordinate reference system;
- geometry source;
- boundary validity date;
- spatial resolution;
- disputed or uncertain boundary status where applicable; and
- version.

### 7.3 Burkina Faso identifiers

Burkina Faso data must preserve official national and subnational identifiers where available. Crosswalks to international codes may be added but may not replace the authoritative national identifier.

## 8. Time contract

Every temporal record must distinguish among:

- observation time;
- publication time;
- validity period;
- model base year;
- planning period;
- representative time slice;
- scenario horizon; and
- data-access date.

Temporal aggregation must be documented. Annual values may not be silently treated as hourly profiles. Representative time slices must retain weights that reconstruct the modeled period.

## 9. Unit conventions

### 9.1 General rule

All dimensional variables must use an approved unit and preserve the original unit in source metadata.

### 9.2 Initial preferred units

| Quantity | Preferred unit |
|---|---|
| Electrical power | `kW`, `MW` or `GW` with scale explicit |
| Electrical energy | `kWh`, `MWh`, `GWh` or `TWh` with scale explicit |
| Thermal energy | `MJ`, `GJ` or `TJ` |
| Fuel mass | `kg`, `t` |
| Fuel volume | `L`, `m3` |
| Distance | `m`, `km` |
| Area | `m2`, `km2`, `ha` |
| Time | `h`, `day`, `year` |
| Monetary value | Currency code plus price year and real/nominal status |
| Emissions | `kgCO2e`, `tCO2e` |
| Reliability | Defined metric-specific unit, never generic percent without definition |

Currency records must include currency, price year, exchange-rate basis where used, and whether values are real or nominal.

## 10. Missing-data contract

Allowed missing statuses are:

- `not_missing`
- `not_collected`
- `unavailable`
- `suppressed`
- `not_applicable`
- `imputed`
- `below_detection_limit`

Imputed values must include:

- imputation method;
- input records;
- uncertainty;
- responsible reviewer;
- reason for use; and
- validation status.

Zero must never be used to represent missingness.

## 11. Uncertainty contract

Uncertainty may be represented as:

- minimum and maximum;
- mean and standard deviation;
- confidence interval;
- probability distribution;
- scenario set;
- sensitivity range; or
- qualitative confidence class.

The uncertainty representation must match the evidence. False numerical precision is prohibited.

## 12. Scenario contract

Every scenario must include:

- `scenario_id`;
- name;
- version;
- purpose;
- geographic scope;
- base year;
- planning horizon;
- policy assumptions;
- demand assumptions;
- technology assumptions;
- financing assumptions;
- deployment assumptions;
- climate and hazard assumptions;
- canonical data release;
- status; and
- responsible owner.

Allowed scenario statuses are `draft`, `reviewed`, `approved`, `superseded` and `rejected`.

## 13. Model-run contract

Every run must record:

- `run_id`;
- scenario identifier;
- model implementation and version;
- repository commit;
- canonical data release;
- solver and version;
- solver options and tolerances;
- execution environment;
- execution timestamp;
- termination condition;
- feasibility status;
- objective value where applicable;
- output location;
- verification report identifier; and
- responsible operator.

Results without a valid run record are not approved dashboard inputs.

## 14. Canonical dataset families

### 14.1 Geography and settlements

- administrative boundaries;
- settlement locations;
- population;
- density;
- urban or rural classification;
- accessibility and remoteness.

### 14.2 Critical public facilities

- health facilities;
- schools;
- water and sanitation systems;
- emergency and public-service facilities;
- service requirements and critical loads.

### 14.3 Demand

- observed electricity demand;
- unserved demand;
- suppressed demand;
- household service demand;
- productive-use demand;
- critical-service demand;
- future development demand;
- load profiles and flexibility.

### 14.4 Infrastructure

- generation assets;
- transmission and distribution networks;
- substations;
- mini-grids;
- stand-alone systems;
- storage;
- imports and interconnections;
- condition and availability.

### 14.5 Technologies and resources

- technical performance;
- existing capacity;
- candidate capacity;
- resource potential;
- capacity factors or profiles;
- degradation;
- lifetime;
- construction and maintenance requirements.

### 14.6 Costs and finance

- capital cost;
- fixed and variable operating cost;
- fuel and import cost;
- financing terms;
- taxes and duties;
- exchange-rate exposure;
- price year and currency.

### 14.7 Reliability and resilience

- outage frequency and duration;
- availability;
- firm capacity;
- critical-service continuity;
- hazard exposure;
- recovery time;
- redundancy;
- backup autonomy.

### 14.8 Deployment

- approval times;
- procurement lead times;
- supply-chain constraints;
- workforce availability;
- construction duration;
- commissioning requirements;
- maintenance readiness;
- spare-parts availability.

### 14.9 Local capability and sovereignty

- local ownership;
- African engineering participation;
- local or regional manufacturing;
- operations and maintenance capability;
- import dependency;
- fuel dependency;
- spare-parts dependency;
- data ownership;
- technology and knowledge access.

### 14.10 Policy and institutional constraints

- access targets;
- renewable targets;
- import limits;
- reliability standards;
- tariffs and subsidies;
- local-content requirements;
- environmental and land constraints;
- institutional responsibilities.

## 15. Data-zone rules

| Zone | Purpose | Rule |
|---|---|---|
| `raw` | Permitted immutable source copies | Never overwritten |
| `external` | Externally maintained reference material | Preserve source identity |
| `interim` | Documented transformations not yet approved | Not used for final decisions |
| `canonical` | Validated platform-independent records | Authoritative downstream interface |
| `processed` | Model- or report-ready outputs derived from canonical data | Must retain lineage |
| `catalog` | Source, dataset and release metadata | Required for discoverability and licensing |

## 16. Adapter requirements

Each tool adapter must:

1. read canonical records;
2. validate required fields and units;
3. transform without changing scientific meaning;
4. record mappings and defaults;
5. reject unsupported or ambiguous records;
6. create a reproducible transformation log;
7. preserve canonical identifiers in outputs.

An adapter may not create hidden assumptions.

## 17. Quality controls

Minimum controls include:

- schema validation;
- identifier uniqueness;
- referential integrity;
- unit validation;
- valid geographic hierarchy;
- temporal consistency;
- provenance completeness;
- licence completeness;
- range and domain checks;
- duplicate detection;
- missingness checks;
- transformation reproducibility;
- version consistency.

## 18. Sensitive-data controls

Sensitive records may require:

- access restrictions;
- spatial aggregation;
- coordinate masking;
- removal of personal identifiers;
- institutional authorization;
- retention limits; and
- security classification.

The public dashboard must never expose sensitive infrastructure or personal information merely because it exists in the canonical system.

## 19. Ownership and review

Each canonical dataset family must have:

- a data owner;
- a technical steward;
- a domain reviewer;
- a validation status;
- an update frequency; and
- a documented escalation path for disputed values.

Owners for Burkina Faso datasets are unresolved and must be assigned in `DATA-001`.

## 20. Frozen decisions

- Canonical data are authoritative downstream.
- Canonical records are independent of platform-specific structures.
- Original source metadata and licensing are mandatory.
- Facts, assumptions and scenarios remain separate.
- Missingness, uncertainty and validation states are explicit.
- energyRt and Pyomo must consume equivalent canonical inputs for benchmark cases.
- Dashboard outputs must link to canonical data releases and model-run identifiers.

## 21. Follow-on schema work

Issue #3 lists JSON schemas for geography, demand, technologies, resources, infrastructure, policies and sources. Those schema files require a separately approved implementation step after this contract is reviewed. They are not created in this six-document architecture branch.
