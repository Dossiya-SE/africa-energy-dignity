# Energy Access Explorer Benchmark for Africa Energy Dignity

**Document ID:** `AED-BENCH-EAE-001`  
**Version:** `0.1-draft`  
**Status:** Architecture approval candidate  
**Issue:** `ARCH-001` / Issue #3  
**Initial application:** Burkina Faso

## 1. Purpose

This document defines how Africa Energy Dignity (AED) will evaluate and use the World Resources Institute's Energy Access Explorer (EAE) without duplicating its role, weakening provenance controls or allowing a platform-specific data structure to control AED architecture.

EAE is treated as an upstream geospatial planning benchmark and source-discovery instrument. AED remains responsible for canonical data validation, energy-system optimization, sovereignty and dignity mathematics, deployment engineering and verified decision support.

## 2. Approved strategic role

EAE may support AED in five areas:

1. **Layer discovery** — identify potentially relevant geospatial evidence.
2. **Spatial diagnosis** — visualize relationships among access, population, facilities, infrastructure, resources and productive activity.
3. **Geographic prioritization** — test transparent combinations of spatial criteria.
4. **Method benchmark** — study map organization, filtering, buffering, weighting and multi-criteria workflows.
5. **Source-register development** — trace displayed layers back to original publishers and datasets.

EAE is not the AED canonical database, optimization engine, deployment scheduler or final authority for Burkina Faso recommendations.

## 3. Benchmark questions

The Burkina Faso benchmark must answer:

- Is Burkina Faso currently supported directly in EAE?
- Which geographic resolutions are available?
- Which demand, supply, infrastructure, social-service and productive-use layers are available?
- What is the original source of each relevant layer?
- What are the date, unit, licence and limitations of each layer?
- Which layers are suitable only for screening?
- Which layers may become canonical after independent validation?
- How are criteria normalized, weighted and combined?
- Are weights and thresholds exportable and reproducible?
- What outputs can be legally and technically exported?
- Which EAE capabilities should AED integrate, reference or avoid duplicating?

## 4. Capability assessment matrix

The benchmark must inspect at least the following.

| Capability | Assessment question | AED decision |
|---|---|---|
| Country coverage | Is Burkina Faso available and complete? | Use, supplement or exclude |
| Administrative boundaries | Which levels and vintages are used? | Map to canonical geography IDs |
| Population and settlements | What source, year and resolution? | Validate for spatial demand analysis |
| Electricity infrastructure | Are networks, substations, plants and access status represented? | Use only after source and sensitivity review |
| Health facilities | What facility types and completeness? | Evaluate for critical-service mapping |
| Schools | What facility types and completeness? | Evaluate for education-service mapping |
| Water infrastructure | Are water points, pumping or treatment assets represented? | Determine suitability for critical-load analysis |
| Agriculture | Which crops, irrigation, markets or processing indicators exist? | Evaluate for productive-use analysis |
| Enterprises and industry | Are economic or productive clusters represented? | Determine whether local sources are required |
| Renewable resources | Which solar, wind, hydro or bioenergy layers exist? | Validate against specialized resource datasets |
| Roads and accessibility | What network and travel-time assumptions are used? | Evaluate for logistics and deployment planning |
| Poverty and socioeconomic data | What definitions and dates are used? | Avoid silent use as affordability proxies |
| Multi-criteria analysis | How are values transformed, normalized and weighted? | Reproduce method before use |
| Export capability | Can source data, criteria or outputs be exported? | Record permitted workflows |
| Attribution | What acknowledgement is required? | Enforce in source and output records |
| API or programmatic access | Is a documented supported interface available? | Do not assume undocumented access |

## 5. Burkina Faso priority-analysis use cases

Subject to availability and validation, EAE may support screening for:

### 5.1 Critical public services

Identify areas where health facilities, schools or water services coincide with weak or absent electricity access.

### 5.2 Productive agriculture

Identify agricultural zones where energy could enable irrigation, processing, milling, refrigeration, cold chains or market access.

### 5.3 Settlement electrification

Identify settlement clusters where population, distance to infrastructure, demand potential and accessibility support comparison of grid extension, mini-grid and stand-alone pathways.

### 5.4 Infrastructure resilience

Identify facilities and settlements exposed to heat, flood, drought, wildfire or access disruption when approved hazard layers are available.

### 5.5 Rapid-deployment logistics

Combine roads, settlement access, infrastructure proximity and candidate demand zones to estimate logistical difficulty. EAE outputs may screen locations, but deployment durations require separate engineering evidence.

## 6. Layer-adoption protocol

A displayed EAE layer enters AED only through the following sequence:

```text
Layer observed in EAE
        ↓
Original publisher and dataset identified
        ↓
Licence and attribution verified
        ↓
Source obtained through an approved method
        ↓
Definitions, units, geography and date checked
        ↓
Limitations and uncertainty recorded
        ↓
Independent consistency checks completed
        ↓
Transformation into AED canonical format
        ↓
Validation status assigned
```

A screenshot, map color or manually read value is never sufficient for canonical adoption.

## 7. Required layer-adoption record

For every candidate layer, record:

- AED source identifier;
- EAE display name;
- original dataset name;
- original publisher;
- original URL or persistent identifier;
- EAE access date;
- source access date;
- geographic coverage;
- coordinate reference system;
- spatial resolution;
- temporal coverage;
- variable definition;
- unit;
- licence;
- attribution text;
- processing or aggregation performed by EAE if documented;
- known limitations;
- proposed AED use;
- evidence class;
- validation status; and
- responsible reviewer.

## 8. Multi-criteria analysis controls

EAE multi-criteria outputs may inform geographic screening only when AED records:

- criteria selected;
- inclusion and exclusion rules;
- thresholds;
- transformations;
- normalization method;
- weights;
- spatial buffers;
- missing-data treatment;
- sensitivity analysis; and
- output date and platform version where available.

A priority score is a decision aid, not an observed fact. It must be labeled as derived or scenario-based.

## 9. Integration boundary

### 9.1 Allowed integration

- Manual, documented benchmark of platform capabilities.
- Approved export or original-source acquisition.
- Adapter from legally obtained source data into AED canonical records.
- Citation and attribution of EAE methods or outputs.
- Use of EAE-derived priority zones as candidate model geographies after validation.

### 9.2 Disallowed integration

- Unauthorized scraping.
- Dependence on undocumented internal APIs.
- Embedding EAE as the AED dashboard without architecture review.
- Treating EAE identifiers as canonical AED identifiers.
- Feeding EAE visual outputs directly into energyRt or Pyomo.
- Presenting EAE priority outputs as final project selection.

## 10. Differentiation from AED

| Domain | EAE role | AED extension |
|---|---|---|
| Spatial diagnosis | Primary benchmark | Canonical validation and country-specific synthesis |
| Layer discovery | Strong role | Source governance and licensing register |
| Multi-criteria prioritization | Geographic screening | Sensitivity-tested and versioned AED prioritization |
| Capacity expansion | Not the primary purpose | energyRt and Pyomo modeling |
| Dispatch and storage | Not the primary purpose | Conventional energy-system models |
| Reliability | Spatial indicators where available | Explicit service and system constraints |
| Energy sovereignty | Not the central framework | Ownership, dependency, capability and control variables |
| Rapid deployment | Early-stage planning support | Finance, procurement, workforce, construction and commissioning model |
| Cross-model verification | Outside scope | Mandatory AED validation layer |
| Dashboard | EAE platform interface | Integrated AED evidence, model and deployment decision layer |

## 11. Verification requirements

Before an EAE-derived layer is used for Burkina Faso modeling:

- source identity must be verified;
- geographic alignment must be tested;
- unit and definition must be confirmed;
- time relevance must be assessed;
- missingness and completeness must be evaluated;
- sensitivity to spatial resolution must be considered;
- duplication with national data must be reconciled;
- licence and attribution must be approved;
- canonical transformation must pass validation.

## 12. Required outputs for `GEO-001`

The follow-on benchmark issue must produce:

- a Burkina Faso EAE capability matrix;
- an inventory of relevant layers;
- a complete source and attribution register;
- a geographic-resolution assessment;
- a multi-criteria method record;
- a gap analysis;
- recommended canonical adapters;
- a list of functions AED should not duplicate; and
- unresolved licensing, coverage and quality risks.

## 13. Acceptance criteria

This benchmark is approved when:

- EAE's role is limited to the approved upstream boundary;
- every proposed layer is linked to an original source;
- no undocumented API is assumed;
- attribution requirements are explicit;
- multi-criteria results are classified as derived or scenario outputs;
- Burkina Faso gaps are documented;
- downstream model inputs require canonical validation.

## 14. References

- Energy Access Explorer tool: https://www.energyaccessexplorer.org/tool/s/
- Energy Access Explorer training and methodology: https://training.energyaccessexplorer.org/about/
- Energy Access Explorer attribution guidance: https://www.energyaccessexplorer.org/attribution/
