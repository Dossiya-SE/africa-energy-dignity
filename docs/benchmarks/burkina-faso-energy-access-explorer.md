# Burkina Faso Energy Access Explorer Benchmark

**Document ID:** `AED-BENCH-EAE-BFA-001`  
**Version:** `0.1`  
**Status:** Proposed benchmark for review  
**Issue:** `GEO-001` / Issue #12  
**Geographic scope:** Burkina Faso  
**Platform access date:** 2026-07-30

## 1. Executive assessment

Energy Access Explorer (EAE) is an open-source, interactive geospatial planning platform led by the World Resources Institute (WRI). Its documented role is to combine energy-supply, demographic, social-service and productive-use evidence through map overlays, filters, buffers and multi-criteria analysis. WRI states that EAE synthesizes more than 50 geographic datasets per supported geography and that original-source details are available through metadata controls inside the platform.

This benchmark did **not** confirm an authoritative Burkina Faso country catalogue or a complete Burkina Faso layer inventory. The public tool landing page was accessible only as a desktop-oriented interactive application, while the accessible official documentation did not publish a machine-readable list of supported countries or country-specific layers. WRI describes EAE as available in 15 countries, but the reviewed official pages did not identify Burkina Faso as one of them.

Accordingly:

- Burkina Faso support is classified as **unverified**;
- every requested layer category is recorded as **unknown pending direct authenticated desktop inspection or written confirmation from WRI**;
- no displayed map, inferred endpoint, undocumented service or third-party reproduction is treated as evidence of availability;
- no dataset is downloaded, ingested or converted into an AED model input;
- EAE remains useful as a methodology and interface benchmark even if Burkina Faso is not currently implemented.

The principal GEO-001 result is therefore a controlled verification plan and source-governance boundary for DATA-001, not a claim that specific Burkina Faso datasets are available in EAE.

## 2. Platform role inside AED

EAE should remain an upstream instrument for:

1. layer discovery;
2. visual spatial diagnosis;
3. transparent geographic screening;
4. study of filtering, buffering and multi-criteria workflows;
5. discovery of original publishers and dataset links.

EAE must not become:

- AED's canonical database;
- the authority for Burkina Faso geographic identifiers;
- an optimization engine;
- a source of model-ready values read from maps;
- the final authority for investment or electrification recommendations;
- an undocumented programmatic dependency.

The approved adapter boundary is:

```text
EAE layer or method observed
        ↓
Original publisher identified
        ↓
Original dataset obtained lawfully
        ↓
Licence, definitions, date and resolution verified
        ↓
Country-specific consistency checks
        ↓
AED canonical source record
        ↓
Validated downstream analysis
```

## 3. Burkina Faso layer inventory

### 3.1 Verification status

| Assessment area | Burkina Faso availability in EAE | Evidence status | GEO-001 decision |
|---|---|---|---|
| Country workspace | Unknown | No authoritative public Burkina Faso catalogue located | Obtain direct platform or WRI confirmation |
| Administrative boundaries | Unknown | Country-specific metadata not accessible in reviewed documentation | Verify boundary source and vintage before use |
| Population | Unknown | EAE generally uses demographic data, but Burkina layer not confirmed | Treat only as a candidate category |
| Settlements and built-up areas | Unknown | No Burkina-specific layer metadata confirmed | Verify original settlement product |
| Health facilities | Unknown | EAE supports health-service planning conceptually | Confirm facility source, types and completeness |
| Education facilities | Unknown | EAE supports education-service planning conceptually | Confirm school source, levels and completeness |
| Water services | Unknown | No Burkina-specific water layer confirmed | Consult national water institutions separately |
| Electricity access | Unknown | General EAE supply/demand framework documented | Verify definition, year and spatial method |
| Generation infrastructure | Unknown | No Burkina-specific plant inventory confirmed | Obtain authoritative plant register |
| Transmission network | Unknown | No Burkina-specific network layer confirmed | Obtain SONABEL/WAPP-authorized evidence |
| Distribution network | Unknown | No Burkina-specific network layer confirmed | Obtain SONABEL/ABER-authorized evidence |
| Solar resource | Unknown | Renewable-resource layers are part of EAE's general method | Verify original resource model and resolution |
| Wind resource | Unknown | No Burkina-specific layer confirmed | Verify original resource model |
| Hydropower or water-energy resource | Unknown | No Burkina-specific layer confirmed | Use basin and national evidence if required |
| Biomass or bioenergy resource | Unknown | No Burkina-specific layer confirmed | Require explicit methodology and sustainability limits |
| Agriculture and irrigation | Unknown | Productive-use and agriculture are documented EAE use areas | Verify crop, irrigation and season definitions |
| Productive-use activity | Unknown | EAE supports productive-use screening conceptually | Require local value-chain and enterprise evidence |
| Roads and accessibility | Unknown | Accessibility is relevant to EAE-style screening | Verify road vintage, class and routing assumptions |
| Markets and logistics | Unknown | No Burkina-specific market layer confirmed | Obtain national or validated open-source evidence |
| Poverty and socioeconomic indicators | Unknown | EAE generally uses socioeconomic evidence | Do not use as affordability proxy without validation |
| Climate and hazards | Unknown | EAE can support climate-resilience applications | Verify hazard model, return period and date |

### 3.2 Interpretation

`Unknown` does not mean that the layer is absent. It means that GEO-001 did not obtain sufficient authoritative evidence to classify it as present, current, licensed and usable for Burkina Faso.

A direct desktop inspection must record, for every visible Burkina Faso layer:

- exact EAE display name;
- metadata text;
- original dataset title;
- original publisher;
- original source link;
- year or temporal coverage;
- spatial resolution;
- unit and variable definition;
- licence and attribution requirement;
- export status;
- processing performed by EAE;
- known limitations.

## 4. Source and publisher inventory

EAE is the platform provider, not automatically the original publisher of displayed datasets. WRI's documentation states that original-source details can be reached through the information control associated with each layer.

The following institutions are priority authorities for independent Burkina Faso verification. Inclusion here does not assert that their data are currently displayed in EAE.

| Evidence domain | Priority original authority or custodian | Required verification |
|---|---|---|
| National electricity network, plants, substations and service areas | Société Nationale d'Électricité du Burkina (SONABEL) | Official network vintage, voltage classes, operational status, confidentiality and reuse rights |
| Rural electrification, mini-grids and target localities | Agence Burkinabè de l'Électrification Rurale (ABER) | Project status, locality identifiers, technology, commissioning date and licence |
| National energy policy and sector statistics | Ministry responsible for energy | Official definitions, reporting period and institutional approval |
| Population, census, settlements and socioeconomic indicators | Institut National de la Statistique et de la Démographie (INSD) | Census vintage, administrative geography, estimates and dissemination terms |
| Health facilities | Ministry responsible for health | Facility registry, service type, operational status, coordinates and update process |
| Schools and education facilities | Ministry responsible for education | School registry, education level, operational status and coordinate quality |
| Water infrastructure and services | Ministry and national agencies responsible for water and sanitation | Asset type, operating status, service population and data restrictions |
| Roads and transport accessibility | Ministry and agencies responsible for transport and road infrastructure | Road class, condition, accessibility assumptions and update date |
| Agriculture, irrigation, markets and processing | Ministry responsible for agriculture and national agricultural agencies | Crop season, irrigation status, productive assets, market definitions and survey design |
| Regional transmission and interconnection | West African Power Pool and ECOWAS institutions | Regional network vintage, planned-versus-existing status and reuse rights |
| Solar resource | Original satellite/model provider identified by EAE; specialized reference products for comparison | Model period, grid resolution, uncertainty and licence |
| Climate and hazards | Original meteorological, hydrological or earth-observation publisher | Hazard definition, temporal window, return period, bias correction and licence |

ABER identifies itself as the national institution responsible for rural electrification and for promoting equitable electricity coverage in rural Burkina Faso. This makes ABER a required source-verification authority for rural-electrification and mini-grid evidence, regardless of whether EAE displays an ABER-derived layer.

## 5. Licence and attribution assessment

WRI requires visible attribution when users refer to or use EAE's concept, methods, code, data or analyses. The official attribution page provides distinct formulations for:

- EAE open-source code;
- data accessed through EAE;
- analyses carried out using EAE;
- the EAE methodology technical note.

AED must apply two separate licence checks:

1. **Platform and method rights** — terms governing EAE's code, method and interface.
2. **Dataset rights** — the licence and attribution obligations of every original dataset publisher.

An open-source platform does not automatically make every hosted dataset open for unrestricted redistribution. No candidate layer may enter DATA-001 until its original licence is recorded. Where licence information is absent, ambiguous or only implied by platform availability, the source status must remain `licence_unknown` and ingestion must be blocked.

Required attribution record:

```text
Platform: Energy Access Explorer, World Resources Institute
Platform access date: 2026-07-30
Dataset: exact original dataset title
Original publisher: exact institution
Original source: persistent URL or identifier
Original licence: exact licence or terms
EAE attribution: exact required wording
AED transformation: documented separately
```

## 6. Spatial-resolution assessment

EAE documentation states that the platform can host datasets in different resolutions, scales and formats. Therefore no single spatial resolution should be assumed for all layers.

For Burkina Faso, resolution must be assessed at three levels:

- **native resolution** of the original dataset;
- **EAE processing or display resolution**;
- **AED analysis resolution** after lawful acquisition and validation.

Required checks include:

- raster cell size or vector positional scale;
- coordinate reference system;
- administrative-boundary vintage;
- point-coordinate accuracy for facilities;
- aggregation and resampling method;
- edge effects and no-data treatment;
- suitability for national, regional, provincial, communal or locality analysis.

A coarse national raster may support screening but must not be interpreted as a site-level measurement. Facility points without documented geocoding accuracy must not be used for engineering design or connection-distance calculations.

## 7. Temporal-coverage assessment

Every layer must record:

- observation year or period;
- publication or release date;
- update frequency;
- whether it represents existing, planned or historical infrastructure;
- whether seasonal or monthly variation exists;
- whether the platform has transformed multiple years into one display.

Temporal mismatch is a critical risk. Population estimates, facility registries, electricity networks, road conditions and climate hazards may refer to different years. Multi-layer overlays must not be interpreted as a simultaneous observed system unless the temporal mismatch is explicitly assessed.

No EAE layer should be called `current` merely because it is currently visible on the platform.

## 8. Export and programmatic-access assessment

The accessible EAE analysis interface displays an `Export` function and supports saving and sharing analyses. GEO-001 did not test the contents, formats or licensing scope of exports because no Burkina Faso workspace was authoritatively confirmed.

The 2019 technical note describes a web architecture using a database/API layer and browser clients. That architectural description is not authorization to call an undocumented production endpoint. AED must not infer a supported API from internal implementation details.

Programmatic-access status for Burkina Faso is therefore:

| Capability | Status |
|---|---|
| Documented public Burkina Faso API | Not identified |
| Authorized automated download | Not verified |
| Manual export through interface | Platform function visible; Burkina content and format unverified |
| Saved/shareable analysis | General platform capability visible |
| Undocumented endpoint use | Prohibited |
| Automated scraping | Prohibited without explicit authorization |

Any future automated adapter requires published documentation or written permission, stable identifiers, rate limits, licence review and reproducibility tests.

## 9. Data-quality and uncertainty risks

### 9.1 Coverage uncertainty

Burkina Faso support and layer completeness are unverified. Absence from the reviewed public documentation must not be interpreted as proof of absence from the interactive platform.

### 9.2 Publisher ambiguity

Platform provider, data processor and original publisher may differ. Each role must be recorded independently.

### 9.3 Temporal mismatch

Layers from different years may create false spatial relationships or obsolete infrastructure conclusions.

### 9.4 Resolution mismatch

Combining point, vector and raster evidence at different scales may create artificial precision.

### 9.5 Facility-registry incompleteness

Health, education, water and productive-use facilities may be missing, duplicated, closed, relocated or inaccurately geocoded.

### 9.6 Infrastructure-status ambiguity

Existing, under-construction, planned, decommissioned and proposed assets must not be merged into one category.

### 9.7 Remote-sensing uncertainty

Population, settlements, night lights, land cover and resource estimates are modeled products. Their uncertainty and validation context must be preserved.

### 9.8 Multi-criteria subjectivity

Weights, thresholds and normalization choices produce scenario-dependent priority surfaces. A priority score is a derived decision aid, not an observed fact.

### 9.9 Security and conflict sensitivity

Some infrastructure coordinates or operational details may be restricted. AED must not publish sensitive data merely because they are discoverable.

### 9.10 Licence uncertainty

Unknown or conflicting terms block canonical ingestion and redistribution.

## 10. Missing-data analysis

Even a complete EAE-style geospatial catalogue would not by itself satisfy AED requirements. DATA-001 will still need verified evidence for:

- installed and dependable generation capacity;
- plant operational status and outages;
- transmission and distribution constraints;
- electricity imports and regional trade;
- demand profiles and suppressed demand;
- critical-facility service requirements;
- technology costs and financing parameters;
- fuel supply and strategic dependencies;
- storage characteristics;
- reliability and resilience parameters;
- climate exposure linked to infrastructure failure modes;
- procurement, workforce and construction constraints;
- local capability and maintainability;
- deployment times and approval processes;
- uncertainty ranges and scenario definitions.

These are not safely derivable from map screenshots or generalized global layers.

## 11. Recommended AED uses

Subject to direct verification, EAE may support:

- discovery of candidate data sources;
- visual comparison of settlements, facilities, access and resources;
- preliminary identification of evidence gaps;
- transparent geographic screening;
- development of candidate subnational zones;
- study of multi-criteria workflows and sensitivity requirements;
- communication of non-model, clearly labelled exploratory maps.

Candidate layers may become canonical only after original-source acquisition, licence verification, definition checks, country validation and schema validation.

## 12. Functions AED should not duplicate

AED should not reproduce EAE's general-purpose:

- browser-based layer exploration;
- generic map-overlay interface;
- generic filtering and buffering controls;
- broad multi-country data-discovery catalogue;
- generic multi-criteria map workflow.

AED should instead extend the workflow through:

- canonical source governance;
- Burkina Faso institutional verification;
- consistent geographic and temporal identifiers;
- energy-system reference modeling;
- native mathematical research models;
- cross-model verification;
- resilience, sovereignty and deployment constraints;
- reproducible decision records.

## 13. Requirements for DATA-001

DATA-001 may begin only after the following minimum evidence package is available.

### 13.1 Platform confirmation

- Written or directly recorded confirmation of whether Burkina Faso is supported.
- Exact platform version or access date.
- Complete Burkina Faso layer list, if available.
- Export and supported-access documentation.

### 13.2 Source register

For each candidate dataset:

- stable AED source ID;
- EAE display name, if applicable;
- original dataset title;
- original publisher;
- original URL or persistent identifier;
- platform and source access dates;
- licence and attribution text;
- variable definition and unit;
- geographic coverage and CRS;
- native and processed resolution;
- temporal coverage and release date;
- processing history;
- uncertainty and limitations;
- confidentiality or security status;
- validation owner;
- proposed AED use;
- validation status.

### 13.3 Institutional verification

- SONABEL review for grid, generation and operational infrastructure.
- ABER review for rural electrification, mini-grids and project localities.
- INSD review for population, census geography and socioeconomic evidence.
- Relevant ministries' review for health, education, water, agriculture, transport and energy policy.
- Regional verification for WAPP and cross-border infrastructure.

### 13.4 Technical verification

- duplicate and missing-record assessment;
- coordinate and boundary checks;
- unit validation;
- temporal-alignment assessment;
- cross-source consistency checks;
- resolution-sensitivity analysis;
- licence approval;
- canonical-schema validation.

## 14. Unresolved questions

1. Is Burkina Faso currently selectable as an EAE geography?
2. If supported, what is the complete current layer inventory?
3. Which layer metadata and original-source links are visible after country selection?
4. Which exports contain source data, derived analysis, metadata or images?
5. Are exports available without registration, and under what terms?
6. Is there a documented supported API for country and layer metadata?
7. Which Burkina Faso institutions contributed data or reviewed essential layers?
8. What administrative-boundary vintage is used?
9. Which layers are national, modeled global products or local institutional datasets?
10. How does EAE record dataset updates and superseded versions?
11. Are multi-criteria weights, transformations and missing-data rules fully exportable?
12. Which data are restricted from redistribution or precise public display?
13. What written confirmation can WRI provide before DATA-001 begins?

## 15. References

Accessed 2026-07-30 unless otherwise stated.

1. World Resources Institute. **Energy Access Explorer — About and methodology.** https://training.energyaccessexplorer.org/about/
2. World Resources Institute. **Energy Access Explorer platform.** https://www.energyaccessexplorer.org/
3. World Resources Institute. **Energy Access Explorer tool.** https://www.energyaccessexplorer.org/tool/s/
4. World Resources Institute. **Energy Access Explorer attribution requirements.** https://www.energyaccessexplorer.org/attribution/
5. Mentis, D., Odarno, L., Wood, D., Jendle, F., Mazur, E., Qehaja, A. and Gassert, F. (2019). **Energy Access Explorer: Data and Methods.** https://africa.wri.org/research/energy-access-explorer-data-and-methods
6. World Resources Institute. **Energy Access and Equitable Development.** https://www.wri.org/energy/energy-access
7. Agence Burkinabè de l'Électrification Rurale. **Présentation de l'ABER.** https://www.aber.bf/aber/presentation/
8. Ministère de l'Énergie, des Mines et des Carrières. **Agence Burkinabè d'Électrification Rurale — missions.** https://www.energie-mines.gov.bf/le-ministere/les-structures/details

## Benchmark conclusion

GEO-001 establishes that EAE is methodologically relevant to AED but that Burkina Faso-specific platform coverage cannot yet be treated as verified evidence. The correct next action is a documented direct platform inspection and/or written WRI confirmation, followed by original-publisher verification. Until that occurs, every Burkina Faso EAE layer remains a candidate discovery item rather than a canonical input.
