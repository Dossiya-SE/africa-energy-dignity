# FIN-001 Deterministic Hashing and Result Lineage Contract

- Document ID: `AED-FIN-LINEAGE-001`
- Version: `FIN-CANONICAL-JSON-1`
- Formula baseline: `FIN-001.1`
- Status: Frozen deterministic lineage baseline
- Issue: `FIN-001 / #22`

## 1. Purpose

This contract defines how AED converts one validated finance scenario into canonical bytes, a reproducible SHA-256 input hash, a deterministic calculation-run identity and indicator-level lineage.

The lineage layer is pure. It performs no database access, network access, clock reads, random generation or implicit transformation.

```text
same validated scenario
+ same formula version
+ same software version
→ same canonical bytes
→ same input hash
→ same calculation-run ID
→ same indicator lineage
```

## 2. Canonicalization version

The canonicalization identifier is:

```text
FIN-CANONICAL-JSON-1
```

Changing any rule in this document requires a new canonicalization version. Existing hashes must never be reinterpreted under a different version.

## 3. Canonical JSON rules

The complete validated `FinanceScenario` is included, including evidence, limitations, uncertainty, identifiers and timestamps.

Serialization rules:

1. UTF-8 JSON;
2. object keys sorted lexicographically;
3. compact separators with no insignificant whitespace;
4. Unicode preserved rather than ASCII-escaped;
5. `null` fields retained;
6. arrays preserve declared order;
7. non-string mapping keys rejected;
8. non-finite numeric values rejected;
9. no environment-dependent locale or timezone behavior.

### 3.1 Decimal values

Decimals use a type-tagged, exponent-free, normalized representation:

```json
{"$decimal":"100"}
```

Therefore `100`, `100.0`, `100.00` and `1E+2` have the same canonical representation. Negative zero is canonicalized to zero.

### 3.2 Datetimes

Datetimes must be timezone-aware. They are converted to UTC and use the `Z` suffix:

```json
{"$datetime":"2026-07-31T04:00:00Z"}
```

Two timezone representations of the same instant therefore hash identically. Naive datetimes are rejected.

### 3.3 Other typed values

Dates and floating-point values, where present in supported auxiliary structures, are type-tagged. Non-finite floats are rejected. Validated FIN-001 monetary and rate inputs remain Decimal values.

## 4. Scenario input hash

The scenario input hash is:

```math
H_{input}=SHA256(CanonicalScenarioBytes)
```

External representation:

```text
sha256:<64 lowercase hexadecimal characters>
```

Any material scenario or evidence change changes the hash. Mapping insertion order, equivalent Decimal scale and equivalent timezone representation do not.

## 5. Deterministic calculation-run identity

A deterministic run identity is content-addressed from:

```text
canonicalization_version
formula_version
input_hash
software_version
```

```math
H_{run}=SHA256(CanonicalJSON(run\ identity\ material))
```

External identifier:

```text
finance.run.sha256.<64 lowercase hexadecimal characters>
```

The identity also records:

```text
scenario_id
scenario_version
formula_version
input_hash
canonicalization_version
software_version
```

A repeated calculation with identical normalized inputs and software version has the same deterministic run identity. A later persistence layer may record separate execution-event IDs and timestamps, but those audit events do not alter the deterministic calculation identity.

## 6. Indicator lineage

Each typed indicator result may carry:

```text
indicator_name
calculation_run_id
scenario_id
scenario_version
formula_version
input_hash
canonicalization_version
software_version
```

Lineage attachment must preserve the indicator value, status, method, tolerance, warnings and diagnostics. Formula versions on the indicator and run identity must match.

## 7. Failure controls

Canonicalization or lineage creation fails for:

- non-finite Decimal or float values;
- naive datetimes;
- unsupported object types;
- non-string mapping keys;
- empty software version;
- empty indicator name;
- formula-version mismatch;
- malformed hashes or run IDs.

No failure is converted to an empty hash, zero, random fallback or timestamp-based identifier.

## 8. Test invariants

The regression suite verifies:

- mapping-order invariance;
- Decimal-scale invariance;
- timezone-equivalent timestamp invariance;
- sensitivity to material inputs and evidence limitations;
- SHA-256 format;
- repeatable calculation-run IDs;
- run-ID sensitivity to software version;
- typed indicator lineage attachment;
- formula mismatch rejection;
- absence of clock or randomness dependencies.

## 9. Exclusions

This contract does not implement:

- database persistence;
- execution audit timestamps;
- API endpoints;
- user-interface rendering;
- digital signatures;
- external timestamp authorities;
- stochastic simulation seeds;
- result overwrite policy.

Those controls belong to subsequent FIN-001 persistence and API stages.
