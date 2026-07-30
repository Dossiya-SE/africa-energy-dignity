# Data Governance

## Required metadata

Every dataset must include:

- Source
- Publisher
- Source URL or identifier
- Geographic coverage
- Temporal coverage
- Collection or publication date
- Variables and units
- Processing steps
- License
- Limitations
- Responsible contributor
- Verification status
- Version

## Data zones

- `raw`: immutable source copies where licensing permits
- `external`: externally maintained reference data
- `interim`: transformed but not analysis-ready
- `processed`: validated analysis-ready outputs

## Rules

- Never overwrite raw data.
- Never commit restricted or confidential data.
- Never remove source attribution.
- Never infer licensing permission.
- Record all transformations in scripts.
- Make processed outputs reproducible from permitted inputs.
