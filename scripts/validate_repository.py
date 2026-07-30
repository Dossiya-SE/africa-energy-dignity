"""Run lightweight repository-structure validation."""

from pathlib import Path
import sys


REQUIRED_FILES = [
    "README.md",
    "PROJECT_SETUP.md",
    "CONTRIBUTING.md",
    "GOVERNANCE.md",
    "docs/project-charter.md",
    "docs/scientific-foundation.md",
    "docs/literature-review-protocol.md",
    "docs/mathematical-framework.md",
    "docs/data-governance.md",
    "docs/verification-validation.md",
    "data/DATA_REGISTER.csv",
    "schemas/geographies.schema.json",
    "schemas/demand.schema.json",
    "schemas/technologies.schema.json",
    "schemas/resources.schema.json",
    "schemas/infrastructure.schema.json",
    "schemas/policies.schema.json",
    "schemas/sources.schema.json",
    "scripts/validate_schemas.py",
]


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    missing = [name for name in REQUIRED_FILES if not (root / name).exists()]

    if missing:
        print("Repository validation failed. Missing:")
        for item in missing:
            print(f"- {item}")
        return 1

    print("Repository structure validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
