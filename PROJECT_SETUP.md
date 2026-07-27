# GitHub Project Setup

## Immediate sequence

1. Create the repository with the name `africa-energy-dignity`.
2. Upload the contents of this package.
3. Link the repository to the GitHub Project named **Africa Energy Dignity**.
4. Configure the custom fields below.
5. Create the first foundation issue using the text in this document.
6. Add the issue to the project and assign its phase, priority and target date.

## Recommended project status values

- Backlog
- Ready
- In Progress
- Technical Review
- Validation
- Blocked
- Completed

## Recommended custom fields

| Field | Type | Values |
|---|---|---|
| Workstream | Single select | Research; Data; Modeling; GIS; Dashboard; Deployment; Governance; Documentation |
| Phase | Single select | Foundation; MVP; Validation; Pilot; Scale |
| Priority | Single select | Critical; High; Medium; Low |
| Geography | Single select | Continental; Regional; Country; Community |
| Country | Text | Country name when applicable |
| Deliverable Type | Single select | Code; Dataset; Model; Paper; Dashboard; Policy; Case Study |
| Evidence Status | Single select | Proposed; Sourced; Verified; Reproducible |
| Risk Status | Single select | On Track; At Risk; Blocked |
| Target Date | Date | Planned completion date |
| Owner | Assignee | Accountable contributor |

## Recommended project views

### 1. Command Center

- Layout: Table
- Group by: Phase
- Sort by: Priority, then Target Date
- Show: Status, Workstream, Phase, Priority, Owner, Target Date, Risk Status

### 2. Execution Board

- Layout: Board
- Column by: Status
- Filter: `status:Backlog,Ready,"In Progress","Technical Review",Validation,Blocked`

### 3. Master Roadmap

- Layout: Roadmap
- Date field: Target Date
- Group by: Phase

### 4. Research and Evidence

- Layout: Table
- Filter: `workstream:Research,Data`
- Group by: Evidence Status

### 5. Country Pilots

- Layout: Table or Roadmap
- Filter: `geography:Country,Community`
- Group by: Country

## First issue

### Title

`FOUNDATION-001 — Approve the project charter, system boundary and 90-day mission`

### Issue body

```markdown
## Objective

Establish the authoritative project charter for Africa Energy Dignity and approve the scope, governance principles, system boundary, scientific requirements and first 90-day mission.

## Why this matters

The project cannot move rapidly without a stable decision baseline. This issue creates the minimum verified foundation required for data architecture, modeling, dashboard design and country-case selection to proceed in parallel.

## Required outputs

- [ ] Approve the project mission and vision
- [ ] Approve the definition of energy dignity
- [ ] Approve the geographic and infrastructure system boundaries
- [ ] Approve the non-negotiable engineering principles
- [ ] Approve the scientific-integrity protocol
- [ ] Approve the verification and validation hierarchy
- [ ] Approve the rapid-deployment stage gates
- [ ] Approve the first 90-day deliverables
- [ ] Assign accountable owners
- [ ] Record unresolved decisions and risks

## Acceptance criteria

- [ ] The project charter is stored in `docs/project-charter.md`
- [ ] Every major term is operationally defined
- [ ] Facts, assumptions and strategic preferences are separated
- [ ] The system boundary is explicit
- [ ] The first 90-day mission contains measurable outputs
- [ ] Each critical deliverable has one accountable owner
- [ ] Open risks and dependencies are documented
- [ ] The charter is reviewed and versioned

## Evidence required

- Project README
- Scientific-foundation document
- Initial literature anchors
- Data-source register
- Governance decision log

## Proposed project fields

- Workstream: Governance
- Phase: Foundation
- Priority: Critical
- Geography: Continental
- Deliverable Type: Policy
- Evidence Status: Proposed
- Risk Status: On Track
```

## Next issues after FOUNDATION-001

1. `RESEARCH-001 — Operationalize and validate the Energy Dignity framework`
2. `RESEARCH-002 — Execute the systematic literature-review protocol`
3. `DATA-001 — Build the authoritative energy and geospatial source register`
4. `DATA-002 — Approve the country energy-data schema`
5. `MODEL-001 — Specify the multi-objective mathematical framework`
6. `MODEL-002 — Define rapid-deployment and time-to-impact metrics`
7. `DASHBOARD-001 — Approve dashboard requirements and information architecture`
8. `PILOT-001 — Select the first country demonstration case`
9. `VANDV-001 — Approve the verification and validation plan`
10. `GOV-001 — Approve contribution, review and decision-rights rules`
